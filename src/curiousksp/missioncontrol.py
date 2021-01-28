"""mission control!"""
import signal
from functools import partial

from loguru import logger

import krpc
import curio
from curio.monitor import Monitor as CurioMonitor


class MissionControl:
    def __init__(self, name="curious",
                 krpc_addr="127.0.0.1", krpc_port=50000, krpcs_port=50001,
                 monitor_port=42047, debuggers=None):
        self._name = name
        self._krpc_addr = krpc_addr
        self._krpc_port = krpc_port
        self._krpcs_port = krpcs_port
        self._monitor_port = monitor_port
        self._debuggers = debuggers

        # TODO: separate the signalling/shutdown_mode aspects into subclass or composite?
        # setup the default shutdown mode, one of "now" | "ask" | "ask soft"
        self._shutdown_mode = "ask"
        # set the default running state
        # TODO: replace running paradigm by making all Tasks cancellable?
        self._running = False
        # init curio.Kernel and curio.monitor.Monitor as None
        self._ck, self._cm = None, None
        # init task refs as None
        self._start_task = None

        # setup a signal so that we can catch KeyboardInterrupt/Ctrl-C and handle them async
        self._sigint_event = curio.UniversalEvent()
        signal.signal(signal.SIGINT, self._handle_sigint)

    # TODO: add properties to guard internals like _name against changes
    def _handle_sigint(self, signo, frame):
        if not self._sigint_event.is_set():
            self._sigint_event.set()

    # TODO: rename to shutdown
    async def _sigint_shutdown(self):
        logger.info(f"Shutting down '{self._name}' mission control...")
        self._running = False
        # cancel tasks
        if self._start_task:
            await self._start_task.cancel()

    async def sigint(self):
        # TODO: replace running paradigm by making all Tasks cancellable?
        while self._running:
            await self._sigint_event.wait()
            self._sigint_event.clear()
            if self._shutdown_mode == "now":
                # signal shutdown as soon as this task picks up the sigint_event it was waiting on
                await self._sigint_shutdown()
            elif self._shutdown_mode.startswith("ask"):
                try:
                    # TODO: this really needs to use some form of async console.readline so it doesn't block :/
                    # atm, this works like a pause while awaiting confirmation or declination to shutdown
                    # because input blocks the Task and thus the curio.Kernel
                    response = input("Ctrl-C! Confirm to end all missions and shutdown mission control? Y/N: ")
                    if response.lower() in ["y", "ye", "yes"]:
                        await self._sigint_shutdown()
                    else:
                        logger.info("Shutdown declined...")
                except EOFError as e:
                    # occurs at Ctrl-C/KeyboardInterrupt triggered when the input prompt is open
                    if self._shutdown_mode == "ask soft":
                        # shutdown for the second Ctrl-C that has triggered
                        await self._sigint_shutdown()
                    else:
                        # ignore the sigint - requiring hard confirmation from user to quit
                        logger.error("Response required, none was given :(")
            else:
                raise ValueError(f"MissionControl._shutdown_mode must be 'now'|'ask'|'ask soft'")

    def _connect(self, name=None, address="127.0.0.1", rpc_port=50000, stream_port=50001):
        logger.info(f"Connecting to kRPC at '{address}' as '{name}' [{rpc_port=}, {stream_port=}]")
        conn = krpc.connect(name=name, address=address, rpc_port=rpc_port, stream_port=stream_port)
        return conn

    async def poll_for_ksp_connect(self):
        # TODO: replace self._running with True and send poll_for_ksp_connect_task.cancel() to end
        # the synchronous parts of this need to run in a separate thread - now it begins...
        try:
            while self._running:
                try:
                    # use a functools.partial here to pass keyword arguments into the synchronous function _connect
                    conn = await curio.run_in_thread(partial(self._connect, name=self._name, address=self._krpc_addr,
                                                             rpc_port=self._krpc_port, stream_port=self._krpcs_port))
                    return conn
                except ConnectionRefusedError as e:
                    # connection refused :(, let's do nothing, wait a bit, and then try again
                    logger.error("Connection refused - is KSP running and is the kRPC server started?")
                    logger.info("Waiting 10 seconds before next KSP/kRPC connection poll attempt...")
                await curio.sleep(10)
        except curio.CancelledError:
            logger.debug("MissionControl.poll_for_ksp_connect cancelled")
            raise

    async def start(self):
        # TODO: add docstrings!
        self._start_task = await curio.current_task()
        try:
            self._running = True
            # setup background task to wait for SIGINT events
            await curio.spawn(self.sigint, daemon=True)
            # TODO: spawn monitor console with subprocess.Popen(NEW_CONSOLE)
            poll_task = await curio.spawn(self.poll_for_ksp_connect)
            conn = await poll_task.join()
            logger.success(f"{conn=}")
            # HACK: experiment with conn: krpc.client.Client in a totally blocking fashion
            print(conn.krpc.get_status())
            print(f"clients:{conn.krpc.clients}")
            # print(f"services=\n {conn.krpc.get_services()}")
            print(f"current game scene: {conn.krpc.current_game_scene}")
            print(f"paused: {conn.krpc.paused}")
            sci, ksd, rep = conn.space_center.science, conn.space_center.funds, conn.space_center.reputation
            print(f"current: sci={sci:.1f}, ksd={ksd:.2f}, rep={rep:.0f}")
            # TODO: spawn heartbeat/status class
            # HACK: run for a while - so we have time to check interaction of sigint etc during dev
            #       when start ends, all other spawned tasks are daemonic; self.run would return immediately
            await curio.sleep(5)
            return "timeout: end of all tasks reached"
            raise NotImplementedError
        except curio.CancelledError:
            # print(f"tracebacks::\n{dir(e.__traceback__)}")
            logger.debug("[cancelled] MissionControl.start! cleaning up:")
            logger.debug(f"Cancelling '{poll_task.name}' [id={poll_task.id}, state={poll_task.state}]...")
            await poll_task.cancel()
            return "cancelled"

    def run(self):
        self._ck = curio.Kernel(debug=self._debuggers, taskcls=curio.task.ContextTask)
        self._cm = CurioMonitor(self._ck, port=self._monitor_port)
        # run the monitor task with the kernel
        # returns None immediately because it is daemonic(?)
        self._ck.run(self._cm.start)
        # create the start(/main) task and run with self._ck
        return self._ck.run(self.start)
