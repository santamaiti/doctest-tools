# setpath.py

import os.path
import sys

def is_package(path):
    r"""Tests whether path is a Python package directory.

    The way it determines this is by checking for an __init__.{py,pyc,pyo}
    file in the directory.
    """
    for suffix in 'py', 'pyc', 'pyo':
        if os.path.exists(os.path.join(path, '__init__.' + suffix)):
            return True
    return False

def setpath(filepath = None, remove_cwd = True, remove_first = False):
    r"""Add the appropriate prefix of filepath to sys.path.

    This searches backwards up the list of directories in filepath looking for
    the first one that is not a Python package directory (i.e., does not
    contain an __init__.py file).  It then adds this final directory to
    Python's path (in sys.path).

    If remove_first is True, it will remove the first entry on sys.path.  This
    is used when called from a script.  When the script is run as "python
    somewhere/foobar.py", python adds the directory containing foobar.py to
    sys.path.  The remove_first option undoes this (albeit blindly -- it
    doesn't do any sanity checks first).  But note that python does _not_ add
    anything to sys.path when called with the '-m' option, for example:
    "python -m somewhere.foobar".  In this case, "somewhere" must have been on
    the python path to begin with for python to even find it in the first
    place...

    If remove_cwd is True, it will remove an '' entry (if any) from sys.path.
    """
    filepath = os.path.abspath(filepath)
    if not os.path.isdir(filepath): filepath = os.path.split(filepath)[0]
    while is_package(filepath): filepath = os.path.split(filepath)[0]
    if remove_first:
        # kill path to this program...
        #sys.stderr.write("removing %r from sys.path\n" % sys.path[0])
        del sys.path[0]
    if remove_cwd and '' in sys.path: sys.path.remove('')
    if filepath in sys.path: sys.path.remove(filepath)
    sys.path.insert(0, filepath)
    return filepath

