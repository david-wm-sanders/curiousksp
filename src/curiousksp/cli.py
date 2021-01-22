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


def main(argv=sys.argv):
    """
    Args:
        argv (list): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    # print(argv)
    # print("hello, start here yo!")
    # print("this is now editable - wooo")
    conn = krpc.connect(name="curiousksp::test")
    # print(conn.krpc.get_status().version)
    print(conn.krpc.get_status())
    # vessel = conn.space_center.active_vessel
    # print(vessel.name)
    time.sleep(5)
    return 0
