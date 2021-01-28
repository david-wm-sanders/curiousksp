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
    curiousksp.py [--addr=<ip>] [--rpc=<port>] [--stream=<port>] [--dbg_task_filter=<a,b,c>] [--dbg_max_time=<float>]
    curiousksp.py _monitor
    curiousksp.py _console
    curiousksp.py _display
    curiousksp.py _control
    curiousksp.py _process

Options:
    --addr=<ip>                IP address of target host running KSP w/ kRPC [default: 127.0.0.1]
    --rpc=<port>               kRPC port [default: 50000]
    --stream=<port>            kRPC stream port [default: 50001]
    --dbg_task_filter=<a,b,c>  Comma-separated list of Task names for curio.debug.schedtrace filter
    --dbg_max_time=<float>     Max time for curio.debug.longblock debugger [default: 0.1]
"""
import sys
import time

from loguru import logger
# from rich.logging import RichHandler
# import curio
# import krpc
from docopt import docopt

from .debug import _configure_debuggers
from .missioncontrol import MissionControl
from .util import _check_connection

# import contextvar
# ksp_conn: ContextVar[krpc.Connection] = ContextVar('ksp_conn', default=None)


@logger.catch
def main(argv=sys.argv):
    """
    Args:
        argv (list): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    # logger.configure(handlers=[{"sink": RichHandler(markup=True), "format": "{message}"}])
    # logger.configure(handlers=[{"sink": RichHandler(), "format": "{message}"}])
    log_fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
              "<level>{level: <8}</level> | " \
              "<level>{message}</level> [<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>]"
    logger.configure(handlers=[{"sink": sys.stderr, "format": log_fmt}])
    logger.add("curiousksp.log", format=log_fmt, retention="7 days", rotation="1 day")
    # enable the library logging for CLI mode
    logger.enable("curiousksp")

    args = docopt(__doc__)
    logger.debug(f"command-line parameters:\n{args}")
    # le basics
    if args["_monitor"]:
        pass

    # TODO: C:\Users\david\AppData\Local\hyper tasks
    # TODO: asynkrpc(?) one day... XD
    # TODO: type anno
    # TODO: process comma-sep debuggers args list of Task names into a set of the Task names

    addr, rpc_port, stream_port = args["--addr"], int(args["--rpc"]), int(args["--stream"])
    debuggers = _configure_debuggers(filter_=args["--dbg_task_filter"], max_time=args["--dbg_max_time"])
    mc = MissionControl(krpc_addr=addr, krpc_port=rpc_port, krpcs_port=stream_port, debuggers=debuggers)
    report = mc.run()
    print(f"{report=}")

    # copied from curio.io for the mo in order to remind me than cancellation handlers can set e.var etc
    # async def readlines(self):
    #         lines = []
    #         try:
    #             async for line in self:
    #                 lines.append(line)
    #             return lines
    #         except errors.CancelledError as e:
    #             e.lines_read = lines
    #             raise

    # [blocking] get the active vessel and print its name
    # vessel = conn.space_center.active_vessel
    # print(vessel.name)

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
