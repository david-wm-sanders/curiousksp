"""Define a Mission Control that bootstraps a curio.Kernel and jumps into the supernova of async/await Tasks."""
# import signal
from functools import partial

from loguru import logger

import krpc
import curio
from curio.monitor import Monitor as CurioMonitor

from .signalling import SignalHandler


# 🏗️  building construction for? MissionControl?
# 🏭  factory for factory patterns, ofc
# 🚨  rotating light for alerts/aborts/emergency action?
# 🚧  construction for DO NOT ENTER, this is where the aliens and the stargate are hidden 🤣  👽 👽 👽
# 🚀  rocket for launchable vessels
# ⭐  star for reputation?, 🌟  star2 for ?
# 💫  dizzy looks like a ring with two marked points on it - peri and apo xd? could represent orbits
# 🔥🔥🔥  fire fire fire up those engines
# 💥  boom for CRITICAL ERRORS ;D - a RUD has occurred
# 🐍  snake for python 3 <3
# 📷  camera for managing ksp game camera
# ⏰  alarm clock for timekeeping tasks
# 📡  satellite though it really looks more like a radio comms dish so maybe communications?
# and more, see https://gist.github.com/rxaviers/7360908 for inspiration
class MissionControl:
    """Defines a MissionControl instance that runs curio.Tasks asynchronously."""

    def __init__(self, name="curious",
                 krpc_addr="127.0.0.1", krpc_port=50000, krpcs_port=50001,
                 monitor_port=42047, debuggers=None):
        """Initialise a new MissionControl instance."""
        self._name = name
        self._krpc_addr = krpc_addr
        self._krpc_port = krpc_port
        self._krpcs_port = krpcs_port
        self._monitor_port = monitor_port
        self._debuggers = debuggers

        # init curio.Kernel and curio.monitor.Monitor as None
        self._ck, self._cm = None, None
        # init task refs as None
        self._start_task = None

        # setup a signal handler to manage Ctrl-C/KeyboardInterrupt initiated shutdown
        self._signal_handler = SignalHandler(self.shutdown, shutdown_mode="ask soft")

    # TODO: add properties to guard internals like _name against changes

    async def shutdown(self):
        """Task: shutdown other running tasks. maybe even save some state first?."""
        logger.info(f"Shutting down '{self._name}' mission control...")
        # self._running is dead in favour of a missioncontrol maintask (like start) being responsible for cancelling
        # the tasks that it manages
        # self._running = False
        # cancel tasks
        if self._start_task:
            await self._start_task.cancel()

    def _connect(self, name=None, address="127.0.0.1", rpc_port=50000, stream_port=50001):
        """[sync] Return krpc.client.Client from blocking krpc.connect."""
        logger.info(f"Connecting to kRPC at '{address}' as '{name}' [{rpc_port=}, {stream_port=}]")
        conn = krpc.connect(name=name, address=address, rpc_port=rpc_port, stream_port=stream_port)
        return conn

    async def connect(self, name, address="127.0.0.1", rpc_port=50000, stream_port=50001):
        """Task: run in thread self._connect and return the constructed krpc.client.Client."""
        # use a functools.partial here to pass keyword arguments into the synchronous function _connect
        conn = await curio.run_in_thread(partial(self._connect, name, address=self._krpc_addr,
                                                 rpc_port=self._krpc_port, stream_port=self._krpcs_port))
        return conn

    async def poll_for_ksp_connect(self):
        """Task: poll for first connection as part of MissionControl.start - waiting 10 seconds before next attempt."""
        # the synchronous parts of this need to run in a separate thread - now it begins...
        try:
            while True:
                try:
                    conn = await self.connect(self._name)
                    return conn
                except ConnectionRefusedError as e:
                    # TODO: do some form of await here to prevent logging of below after shutdown has begun?
                    # connection refused :(, let's output some fancy logs 🐍
                    logger.error("Connection refused - is KSP running and is the kRPC server started?")
                    logger.debug("Waiting 10 seconds before next KSP/kRPC connection poll attempt...")
                # now wait a bit before trying again
                await curio.sleep(10)
        except curio.CancelledError:
            logger.debug("[cancelled] 'MissionControl.poll_for_ksp_connect'")
            raise

    async def heartbeat(self, downtime=3):
        """Task (daemonic): periodically poll krpc for status information and log/display."""
        try:
            # TODO: make a task-local connection
            conn = await self.connect(f"{self._name}:heartbeat")
            # while True: get krpc.status(), print/log nicely, wait a sec or two(?), repeat
            while True:
                # TODO: get status
                s = conn.krpc.get_status()
                # print(status)
                status = f"RPCs: {s.rpcs_executed} [{s.rpc_rate}]; " \
                         f"IO: R: {s.bytes_read}, W: {s.bytes_written}; " \
                         f""
                # print(dir(s))
                # TODO: log nicely
                logger.debug(f"❤️  {status}")
                await curio.sleep(downtime)
        except curio.CancelledError as e:
            logger.debug("[cancelled] 'MissionControl.heartbeat' - cleaning up:")
            # close the conn
            if conn:
                logger.debug("Closing heartbeat connection...")
                conn.close()
            raise

    async def start(self):
        """Task: curio.Kernel.run(start) main that boots up the async parts of MissionControl."""
        self._start_task = await curio.current_task()
        try:
            # setup background task to wait for SIGINT events
            sigint_task = await curio.spawn(self._signal_handler.sigint, daemon=True)
            # TODO: spawn monitor console with subprocess.Popen(NEW_CONSOLE)
            poll_task = await curio.spawn(self.poll_for_ksp_connect)
            conn = await poll_task.join()
            logger.success(f"{conn=}")
            # HACK: experiment with conn: krpc.client.Client in a totally blocking fashion
            # print(conn.krpc.get_status())
            # print(f"clients:{conn.krpc.clients}")
            # # print(f"services=\n {conn.krpc.get_services()}")
            # print(f"current game scene: {conn.krpc.current_game_scene}")
            # print(f"paused: {conn.krpc.paused}")
            # TODO: getting sci, funds, rep etc may fail with RuntimeError depending on game mode
            # sci, ksd, rep = conn.space_center.science, conn.space_center.funds, conn.space_center.reputation
            # print(f"current: sci={sci:.1f}, ksd={ksd:.2f}, rep={rep:.0f}")
            # TODO: spawn heartbeat/status class
            heartbeat_task = await curio.spawn(self.heartbeat, daemon=True)

            # HACK: run for a while - so we have time to check interaction of sigint etc during dev
            #       when start ends, all other spawned tasks are daemonic; self.run would return immediately
            await curio.sleep(5)
            return "timeout: end of all tasks reached"
            raise NotImplementedError
        except curio.CancelledError:
            # print(f"tracebacks::\n{dir(e.__traceback__)}")
            logger.debug("[cancelled] 'MissionControl.start' - cleaning up:")
            logger.debug(f"Cancelling '{sigint_task.name}' [id={sigint_task.id}, state={sigint_task.state}]...")
            await sigint_task.cancel()
            logger.debug(f"Cancelling '{poll_task.name}' [id={poll_task.id}, state={poll_task.state}]...")
            await poll_task.cancel()
            return "cancelled"

    def run(self):
        """Stir this curious cauldron of dark async magic and kerbal witch/wizard blood already!."""
        self._ck = curio.Kernel(debug=self._debuggers, taskcls=curio.task.ContextTask)
        self._cm = CurioMonitor(self._ck, port=self._monitor_port)
        # run the monitor task with the kernel
        # returns None immediately because it is daemonic(?)
        self._ck.run(self._cm.start)
        # create the start(/main) task and run with self._ck
        return self._ck.run(self.start)
