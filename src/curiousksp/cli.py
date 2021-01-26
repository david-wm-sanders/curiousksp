# Module that contains the command line app.
#
# Why does this file exist, and why not put this in __main__?
#
#   You might be tempted to import things from __main__ later, but that will cause
#   problems: the code will get executed twice:
#
#   - When you run `python -mcuriousksp` python will execute
#     ``__main__.py`` as a script. That means there won't be any
#     ``curiousksp.__main__`` in ``sys.modules``.
#   - When you import __main__ it will get executed again (as a module) because
#     there's no ``curiousksp.__main__`` in ``sys.modules``.
#
#   Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""curiousksp.py - ksp chaos with curio coroutines

Usage:
    curiousksp.py [--dbg_task_filter=<a,b,c>] [--dbg_max_time=<float>]
    curiousksp.py _monitor
    curiousksp.py _console
    curiousksp.py _display

Options:
    --dbg_max_time=<float>  Max time for curio.debug.longblock debugger [default: 0.1]
"""
import sys
import time

# import curio
# import krpc
from docopt import docopt

from .debug import _configure_debuggers
from .missioncontrol import MissionControl
from .util import _check_connection

# ahhhh
# from curio.monitor import Monitor as CurioMonitor

# import contextvar
# ksp_conn: ContextVar[krpc.Connection] = ContextVar('ksp_conn', default=None)


# CURIOUS_MONITOR_PORT = 42047


def main(argv=sys.argv):
    """
    Args:
        argv (list): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    # print(dir(curio))

    args = docopt(__doc__)
    print(args)
    # le basics
    # print(argv)
    # TODO: setup docopt
    if args["_monitor"]:
        pass
        # TODO: set up

    # asynkrpc(?) one day... XD

    # [blocking] make a connection to ksp via krpc
    # conn = krpc.connect(name="curious::test")
    # [blocking] get the krpc status
    # print(conn.krpc.get_status())
    # [blocking] get the active vessel and print its name
    # vessel = conn.space_center.active_vessel
    # print(vessel.name)
    # time.sleep(5)

    try:
        debuggers = _configure_debuggers(filter_=args["--dbg_task_filter"], max_time=args["--dbg_max_time"])
        mc = MissionControl(debuggers=debuggers)
        report = mc.run()
        # time.sleep(30)
    except KeyboardInterrupt:
        pass
        # TODO: improve with code to confirm exit and cleanly shutdown MissionControl etc etc


    # Little point in starting everything up if we can't even make a connection to KSP so do a quick check
    # if not _check_connection():
    #     sys.exit("Couldn't make a connection to KSP... exiting.")

    # conn = krpc.connect(name="curious::test")
    # token = ksp_conn.set(conn)
    # vessel = ksp_conn.get().space_center.active_vessel (?)
    # ksp_conn.reset(token)
    # Task._context[ksp_conn] (?)

    # example: using a context copy in another OS thread (contextvars docs)
    # executor = ThreadPoolExecutor()
    # current_context = contextvars.copy_context()
    #
    # executor.submit(current_context.run, some_function)

    # curio'd?:
    # await run_in_thread(current_context.run, some_function, *args) ?

    return 0
