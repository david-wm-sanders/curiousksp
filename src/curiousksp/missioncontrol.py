"""mission control!"""
import signal
from functools import partial

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

        # init curio.Kernel and curio.monitor.Monitor as None
        self._ck, self._cm = None, None
        # setup the default shutdown mode, one of "now" | "ask" | "ask soft"
        self._shutdown_mode = "ask"
        self._running = False

        # setup a signal so that we can catch KeyboardInterrupt/Ctrl-C and handle them async
        self._sigint_event = curio.UniversalEvent()
        signal.signal(signal.SIGINT, self._handle_sigint)

    # TODO: add properties to guard internals like _name against changes
    def _handle_sigint(self, signo, frame):
        if not self._sigint_event.is_set():
            self._sigint_event.set()

    def _sigint_shutdown(self):
        print(f"Shutting down '{self._name}' mission control...")
        self._running = False
        # TODO: signal all tasks to end via Task.cancel here? or in start with self._running or

    async def sigint(self):
        while self._running:
            await self._sigint_event.wait()
            self._sigint_event.clear()
            if self._shutdown_mode == "now":
                # signal shutdown as soon as this task picks up the sigint_event it was waiting on
                self._sigint_shutdown()
            elif self._shutdown_mode.startswith("ask"):
                try:
                    # TODO: this really needs to use some form of async console.readline so it doesn't block :/
                    response = input("Ctrl-C! Confirm to end all missions and shutdown mission control? Y/N: ")
                    if response.lower() in ["y", "ye", "yes"]:
                        self._sigint_shutdown()
                    else:
                        print("Shutdown declined...")
                except EOFError as e:
                    # occurs at Ctrl-C/KeyboardInterrupt triggered when the input prompt is open
                    if self._shutdown_mode == "ask soft":
                        # shutdown for the second Ctrl-C that has triggered
                        self._sigint_shutdown()
                    else:
                        # ignore the sigint - requiring hard confirmation from user to quit
                        print("Response required, none was given :(")
            else:
                raise ValueError(f"MissionControl._shutdown_mode must be 'now'|'ask'|'ask soft'")

    def _connect(self, name=None, address="127.0.0.1", rpc_port=50000, stream_port=50001):
        print(f"Connecting to kRPC at '{address}' as '{name}' [{rpc_port=}, {stream_port=}]")
        conn = krpc.connect(name=name, address=address, rpc_port=rpc_port, stream_port=stream_port)
        return conn

    async def poll_for_ksp_connect(self):
        # TODO: implement ofc :'D
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
                    print("Connection refused - is KSP running and is the kRPC server started?")
                    print("Waiting 10 seconds before polling for a KSP/kRPC connection again...")
                await curio.sleep(10)
        except curio.CancelledError:
            print("async poll_for_ksp_connect cancelled")
            raise

    async def start(self):
        try:
            self._running = True
            # setup background task to wait for SIGINT events
            await curio.spawn(self.sigint, daemon=True)
            # TODO: spawn monitor console with subprocess.Popen(NEW_CONSOLE)
            # TODO: spawn _connection_poll task
            conn_task = await curio.spawn(self.poll_for_ksp_connect)
            conn = await conn_task.join()
            # print(r)
            print(f"{conn=}")
            # HACK: run for a while - so we have time to check interaction of sigint etc during dev
            #       when start ends, all other spawned tasks are daemonic; self.run would return immediately
            await curio.sleep(15)
            # raise NotImplementedError
        except curio.CancelledError as e:
            print("bye bye, MissionControl.start aborted!")
            print(e)

    def run(self):
        self._ck = curio.Kernel(debug=self._debuggers, taskcls=curio.task.ContextTask)
        self._cm = CurioMonitor(self._ck, port=self._monitor_port)
        # run the monitor task with the kernel
        # returns None immediately because it is daemonic(?)
        self._ck.run(self._cm.start)
        # TODO: create the start(/main) task and run with self._ck
        return self._ck.run(self.start)
