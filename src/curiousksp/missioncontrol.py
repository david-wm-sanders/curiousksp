"""mission control!"""
import krpc
import curio
from curio.monitor import Monitor as CurioMonitor


class MissionControl:
    def __init__(self, name="curious", monitor_port=42047, debuggers=None):
        self._name = name
        self._monitor_port = monitor_port
        self._debuggers = debuggers

        self._ck, self._cm = None, None

    async def start(self):
        await curio.sleep(30)
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
