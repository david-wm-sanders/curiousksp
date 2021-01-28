import itertools
# import logging
import time
# import os.path
from pathlib import Path

# import curio
from loguru import logger
from curio.debug import schedtrace as _schedtrace, logcrash as _logcrash, longblock as _longblock


# curio_sched_level = logger.level("CURIO", no=10, color="<yellow>", icon="🌟")
# setup a custom level for curio debugging
curio_sched_level = logger.level("SCHED", no=10, color="<yellow>")

# subclass curio.debug.schedtrace and rewrite to use loguru logger
class schedtrace(_schedtrace):
    @staticmethod
    def _pretty_repr(task):
        location = ""
        filename, lineno = task.where()
        if filename and lineno:
            p = Path(filename)
            # take from reversed path parts while part != "curiousksp" (the module)
            parts = itertools.takewhile(lambda s: s != "curiousksp", p.parts[::-1])
            # reverse so that the submodule dir part is in front of the file part of the filename
            parts = reversed(list(parts))
            filename = ".".join(parts)
            location = f" @ {filename}:{lineno}"
        if task.daemon:
            return f"<{task.id}|{task.cycles}> '{task.name}'{location}"
        else:
            return f"[{task.id}|{task.cycles}] '{task.name}'{location}"
        # return f"<{task.id}|{task.cycles}> '{task.name}'" if task.daemon else f"[{task.id}|{task.cycles}] '{task.name}'"

    def created(self, task):
        # pass on logging anything here to reduce log volume
        pass

    def running(self, task):
        if self.check_filter(task):
            # filename, lineno = task.where()
            # if filename and lineno:
            #     p = Path(filename)
            #     print(f"{p!r}:{lineno}")
            self.log.log(self.level, f"RUN: {self._pretty_repr(task)}")
            # print(f"{task.id}, {task.name}, {task.daemon}, {task.cycles}, {task.where()}")

    def suspended(self, task, trap):
        if self.check_filter(task):
            self.log.log(self.level, f"SUSPEND: {self._pretty_repr(task)}")
            # print(f"{task.id}, {task.name}, {task.daemon}, {task.cycles}, {task.where()}")

    def terminated(self, task):
        if self.check_filter(task):
            self.log.log(self.level, f"TERMINATED: {self._pretty_repr(task)}")
            # print(f"{task.id}, {task.name}, {task.daemon}, {task.cycles}, {task.where()}")


class logcrash(_logcrash):
    pass
    # TODO: need to subclass and override suspended to log with loguru, taking the task.exception as exc_info


class longblock(_longblock):
    def suspended(self, task, trap):
        if self.check_filter(task):
            duration = time.monotonic() - self.start
            if duration > self.max_time:
                # TODO: set up a diff = duration - self.max_time, if diff > threshold: log at higher level
                self.log.log(self.level, f'[longblock] {task!r} ran for {duration:.1f} seconds')


def _configure_debuggers(filter_=None, max_time=0.1):
    logger.debug(f"{filter_=}")
    schedtrace_ = schedtrace(log=logger, level=curio_sched_level.name)
    logcrash_ = logcrash(log=logger)
    longblock_ = longblock(log=logger, level="WARNING", max_time=float(max_time))
    return [schedtrace_, logcrash_, longblock_]
