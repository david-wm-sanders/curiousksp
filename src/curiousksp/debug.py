import logging
import time
from loguru import logger
from curio.debug import schedtrace as _schedtrace, logcrash as _logcrash, longblock as _longblock


# curio_sched_level = logger.level("CURIO", no=10, color="<yellow>", icon="🐍")
# setup a custom level for curio debugging
curio_sched_level = logger.level("SCHED", no=10, color="<yellow>")

# subclass curio.debug.schedtrace and rewrite to use loguru logs
class schedtrace(_schedtrace):
    def created(self, task):
        if self.check_filter(task):
            self.log.log(self.level, f'CREATE: {task!r}')

    def running(self, task):
        if self.check_filter(task):
            self.log.log(self.level, f'RUN: {task!r}')

    def suspended(self, task, trap):
        if self.check_filter(task):
            self.log.log(self.level, f'SUSPEND: {task!r}')

    def terminated(self, task):
        if self.check_filter(task):
            self.log.log(self.level, f'TERMINATED: {task!r}')


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
