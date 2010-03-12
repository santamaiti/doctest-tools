# setpath.py

import os.path
import sys
import glob

def is_package(path):
    r"""Tests whether path is a Python package directory.

    The way it determines this is by checking for an __init__.py* file
    in the directory.
    """
    for _ in glob.iglob(os.path.join(path, '__init__.py*')):
        return True
    return False

def has_package(path):
    r"""Tests whether path contains any Python package directories.

    The way it determines this is by checking for */__init__.py* files.
    """
    for _ in glob.iglob(os.path.join(path, '*', '__init__.py*')):
        return True
    return False

def find_roots(dirpath):
    r"""Generates the root directories to add to sys.path.

    The root directories are generated bottom to top and include the
    bottom-most directory if it's not a package, then all higher directories
    that are not packages themselves, but contain packages.

    dirpath may be either the path to a file or directory.  If it is the path
    to a file, the search starts at the directory containing that file.
    """
    dirpath = os.path.normpath(os.path.abspath(dirpath))
    if not os.path.isdir(dirpath):
        dirpath = os.path.dirname(dirpath)
    lastpath = None
    while dirpath != lastpath:
        # Find first directory without an __init__.py* file.
        while dirpath != lastpath and is_package(dirpath):
            lastpath = dirpath
            dirpath = os.path.dirname(dirpath)
        # dirpath == lastpath or not is_package(dirpath)
        if dirpath == lastpath:
            break
        # not is_package(dirpath)

        # If the first directory was not a package directory, we want it
        # included!
        # Otherwise, we know that this has packages, because we just left one!
        yield dirpath

        lastpath = dirpath
        dirpath = os.path.dirname(dirpath)
        while dirpath != lastpath and not is_package(dirpath):
            if has_package(dirpath):
                # This covers the case where a directory includes packages
                # other than the sub-directory we just came from.
                yield dirpath
            lastpath = dirpath
            dirpath = os.path.dirname(dirpath)
        # dirpath == lastpath or is_package(dirpath)

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

