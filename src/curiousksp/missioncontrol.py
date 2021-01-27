"""mission control!"""
import signal

import krpc
import curio
from curio.monitor import Monitor as CurioMonitor


class MissionControl:
    def __init__(self, name="curious", monitor_port=42047, debuggers=None):
        self._name = name
        self._monitor_port = monitor_port
        self._debuggers = debuggers

        # init curio.Kernel and curio.monitor.Monitor as None
        self._ck, self._cm = None, None
        # setup the default shutdown mode, one of "now" | "ask soft" | "ask hard"
        self._shutdown_mode = "now"
        self._running = False

        self._sigint_event = curio.UniversalEvent()
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _handle_sigint(self, signo, frame):
        if not self._sigint_event.is_set():
            self._sigint_event.set()

    def _sigint_shutdown(self):
        print(f"Shutting down '{self._name}' mission control...")
        self._running = False
        self._sigint_event.clear()

    async def sigint(self):
        while self._running:
            await self._sigint_event.wait()
            try:
                response = input("Keyboard interrupt: are you sure you want to quit? Y/N: ")
                if response.lower() in ["y", "ye", "yes"]:
                    self._sigint_shutdown()
            except EOFError as e:
                # occurs at Ctrl-C/KeyboardInterrupt triggered when the input prompt is open
                # shutdown on second Ctrl-C mode
                self._sigint_shutdown()
                # TODO: clear _sigint_event and ignore mode (effectively a hard confirm shutdown mode)

    async def start(self):
        self._running = True
        # setup background task to wait for SIGINT events
        await curio.spawn(self.sigint, daemon=True)
        # TODO:
        await curio.sleep(15)
        raise NotImplementedError
        # TODO: spawn monitor console with subprocess.Popen(NEW_CONSOLE)
        # TODO: spawn _connection_poll task

    def run(self):
        self._ck = curio.Kernel(debug=self._debuggers, taskcls=curio.task.ContextTask)
        self._cm = CurioMonitor(self._ck, port=self._monitor_port)
        # run the monitor task with the kernel
        # returns None immediately because it is daemonic(?)
        self._ck.run(self._cm.start)
        # TODO: create the start(/main) task and run with self._ck
        return self._ck.run(self.start)
