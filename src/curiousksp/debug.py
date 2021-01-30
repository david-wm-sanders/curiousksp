"""Define curio.debug.DebugBase`s derived from defaults to provide enhanced logging of Kernel task state."""
import inspect
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
curio_sched_level = logger.level("SCHED", no=7, color="<yellow>", icon="🐍")
# TODO: how to make custom level work with RichHandler?
# set of hidden tasks
hidden_tasks = {"Kernel._make_kernel_runtime.<locals>._kernel_task",
                "Monitor.start", "Monitor.monitor_task"}


# subclass curio.debug.schedtrace and rewrite to use loguru logger
class schedtrace(_schedtrace):
    """Subclass curio.debug.schedtrace to output a richer loguru view of the Task scheduling state."""

    @staticmethod
    def _pretty_repr(task):
        """Render beautified Task repr of form: ?id|cycle? where ? is <> if daemon else []."""
        location = ""
        filename, task_lineno = task.where()
        if filename and task_lineno:
            p = Path(filename)
            # take from reversed path parts while part != "curiousksp" (the module)
            parts = itertools.takewhile(lambda s: s != "curiousksp", p.parts[::-1])
            # reverse so that the submodule dir part is in front of the file part of the filename
            parts = reversed(list(parts))
            filename = "/".join(parts)
            # inspect the lines of code for this coroutine and find the single line of code the Task is on
            lines, lineno = inspect.getsourcelines(task.coro.cr_code)
            sloc = lines[task_lineno - lineno]
            # tidy up the sloc by trimming left whitespace and right \n
            sloc = sloc.lstrip().rstrip("\n")
            location = f" @ `{sloc}`[{filename}:{task_lineno}]"
        if task.daemon:
            return f"<{task.id}|{task.cycles}> '{task.name}'{location}"
        else:
            return f"[{task.id}|{task.cycles}] '{task.name}'{location}"

    def created(self, task):
        """Not log Task creation to reduce logging output."""
        # pass on logging anything here to reduce log volume
        pass

    def running(self, task):
        """Log at SCHED level immediately before the next execution cycle of a Task."""
        if self.check_filter(task) and task.name not in hidden_tasks:
            logger.log(self.level, f"▶️  {self._pretty_repr(task)}")

    def suspended(self, task, trap):
        """Log at SCHED level after a Task has suspended due to trap, noting the state e.g. 'FUTURE_WAIT'."""
        if self.check_filter(task) and task.name not in hidden_tasks:
            logger.log(self.level, f"⏸  /{task.state}/ {self._pretty_repr(task)}")

    def terminated(self, task):
        """Log at SCHED level after a Task has terminated but before it is collected (see curio.kernel.Activation)."""
        # if self.check_filter(task) and task.name not in hidden_tasks:
        #     logger.log(self.level, f"⏹  {self._pretty_repr(task)}")
        pass


class logcrash(_logcrash):
    """Subclass curio.debug.logcrash to provide richer loguru output on this quest for sanity."""

    pass
    # TODO: need to subclass and override suspended to log with loguru, taking the task.exception as exc_info


class longblock(_longblock):
    """Subclass curio.debug.longblock to provide rich loguru logging when a Task blocks the kernel for a long time."""

    def suspended(self, task, trap):
        """Log when a Task blocks the kernel for a time > self.max_time."""
        if self.check_filter(task):
            duration = time.monotonic() - self.start
            if duration > self.max_time:
                # TODO: set up a diff = duration - self.max_time, if diff > threshold: log at higher level
                logger.log(self.level, f'🔂  [longblock] {task!r} ran for {duration:.1f} seconds')


def _configure_debuggers(filter_=None, max_time=0.1):
    """Configure subclassed curio.debug.DebugBase`s for loguru logging (via Rich? maybe?)."""
    logger.debug(f"{filter_=}")
    schedtrace_ = schedtrace(level=curio_sched_level.name)
    logcrash_ = logcrash()
    longblock_ = longblock(level="WARNING", max_time=float(max_time))
    return [schedtrace_, logcrash_, longblock_]
