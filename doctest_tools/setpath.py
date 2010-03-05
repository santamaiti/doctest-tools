# setpath.py

import os.path
import sys
import glob

def is_package(path):
    r"""Tests whether path is a Python package directory.

    The way it determines this is by checking for an __init__.py* file
    in the directory.
    """
    try:
        glob.iglob(os.path.join(path, '__init__.py*')).next()
        return True
    except StopIteration:
        return False

def has_package(path):
    r"""Tests whether path contains any Python package directories.

    The way it determines this is by checking for */__init__.py* files.
    """
    try:
        glob.iglob(os.path.join(path, '*', '__init__.py*')).next()
        return True
    except StopIteration:
        return False

def find_root(dirpath, find_package = False):
    r"""Find the first directory that is (not) a package directory.

    dirpath may be either the path to a file or directory.  If it is the path
    to a file, the search starts at the directory containing that file.

    Returns None if no directory is found.
    """
    dirpath = os.path.abspath(dirpath)
    if not os.path.isdir(dirpath):
        dirpath = os.path.dirname(dirpath)
    lastpath = None
    while dirpath != lastpath and is_package(dirpath) != find_package:
        lastpath = dirpath
        dirpath = os.path.dirname(dirpath)
    if dirpath == lastpath:
        return None
    return dirpath

def find_roots(dirpath):
    r"""Generates the root directories to add to sys.path.

    The root directories are generated bottom to top.

    dirpath may be either the path to a file or directory.  If it is the path
    to a file, the search starts at the directory containing that file.
    """
    dirpath = os.path.abspath(dirpath)
    if not os.path.isdir(dirpath):
        dirpath = os.path.dirname(dirpath)
    lastpath = None
    while True:
        # Find first directory without an __init__.py* file.
        while dirpath != lastpath and is_package(dirpath):
            lastpath = dirpath
            dirpath = os.path.dirname(dirpath)
        if dirpath == lastpath:
            break
        yield dirpath       # first directory without an __init__.py* file.
        lastpath = dirpath
        dirpath = os.path.dirname(dirpath)
        while dirpath != lastpath and not is_package(dirpath):
            if has_package(dirpath):
                yield dirpath
            lastpath = dirpath
            dirpath = os.path.dirname(dirpath)

def setpath(filepath, remove_cwd = True, remove_first = False, full = False):
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

    If full is True, the search is done all the way to root adding all
    directories containing packages to sys.path.  (Note that if the first
    directory is not a package, it is also added to sys.path).
    """
    if remove_first:
        # kill path to this program...
        #sys.stderr.write("removing %r from sys.path\n" % sys.path[0])
        del sys.path[0]
    if remove_cwd and '' in sys.path: sys.path.remove('')
    paths = []
    for dirpath in find_roots(filepath):
        if dirpath in sys.path: sys.path.remove(dirpath)
        paths.append(dirpath)
        if not full: break
    sys.path[0:0] = paths
    return paths

