"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mcuriousksp` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``curiousksp.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``curiousksp.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import sys
import time

import curio
import krpc

from .util import _check_connection


# import contextvar
# ksp_conn: ContextVar[krpc.Connection] = ContextVar('ksp_conn', default=None)


def main(argv=sys.argv):
    """
    Args:
        argv (list): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    # le basics
    # print(argv)
    # TODO: setup docopt

    # [blocking] make a connection to ksp via krpc
    # conn = krpc.connect(name="curious::test")
    # [blocking] get the krpc status
    # print(conn.krpc.get_status())
    # [blocking] get the active vessel and print its name
    # vessel = conn.space_center.active_vessel
    # print(vessel.name)
    # time.sleep(5)

    # TODO: make a curio kernel, create a monitor with custom port 34567 default or user specified via docopt
    # ck = curio.Kernel(`opts, debugs, etc`)
    # cm = curio.Monitor(ck, host, port)
    # TODO: add the monitor task to the kernel
    # ck.add_task(cm.start)
    # TODO: create curiousksp.tasks.main and add to kernel
    # ck.add_task(tasks.main, *args)
    # TODO: run the kernel
    # ck.run()


    # Little point in starting everything up if we can't even make a connection to KSP so do a quick check
    if not _check_connection():
        sys.exit("Couldn't make a connection to KSP... exiting.")

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
