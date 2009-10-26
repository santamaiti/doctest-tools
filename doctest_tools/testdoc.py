#!/usr/bin/python

# testdoc.py [-r] file

from __future__ import with_statement

import warnings
import os, os.path
import sys
import doctest
from doctest_tools import setpath

warnings.simplefilter('default')

def import_module(modulepath, remove_first_path = False):
    r"""Imports the module indicated by modulepath.

    Also adds the proper containing directory to Python's sys.path.

    Returns the imported module.
    """
    pythonpath = setpath.setpath(modulepath, remove_first=remove_first_path)
    #sys.stdout.write("setpath: %s\n" % pythonpath)
    modulepath = modulepath[len(pythonpath) + 1:]
    modulename = modulepath.replace('/', '.').replace(os.path.sep, '.')
    module = __import__(modulename)
    for comp in modulename.split('.')[1:]:
        module = getattr(module, comp)
    return module

def test(path, remove_first_path = False):
    r"""Runs doctest on the file indicated by 'path'.

    This will run testmod if the file ends in .py, .pyc or .pyo; and testfile
    for all other files.

    When running testfile, it enables Python's "with" statement (as if the
    file being tested had done "from __future__ import with_statement").  This
    is done because doing the __future__ import does not work in files. :-(

    Also when running testfile, the current working directory is first set to
    the directory containing the file.  This is not done for python modules
    (.py, .pyc or .pyo files).

    In all cases, the lowest level directory not containing an
    __init__.{py,pyc,pyo} file is added to sys.path.  For Python modules, the
    search is started in the directory in containing the module.  For other
    files, the search starts in the current working directory (since
    subdirectories may only contain text files and not contain a __init__.py
    files).
    """
    path = os.path.normpath(path)
    fullpath = os.path.abspath(path)
    if path.endswith('.py'):
        module = import_module(fullpath[:-3], remove_first_path)
    elif path.endswith('.pyc') or path.endswith('.pyo'):
        module = import_module(fullpath[:-4], remove_first_path)
    else:
        setpath.setpath(fullpath[:-(len(path) + 1)],
                        remove_first=remove_first_path)
        os.chdir(os.path.dirname(fullpath))
        return doctest.testfile(fullpath, False,
                                globs={
                                  'with_statement': with_statement,
                                })
    module.doing_doctest = True
    return doctest.testmod(module)

def usage():
    sys.stderr.write("usage: %s [-r] file\n" % os.path.basename(sys.argv[0]))
    sys.exit(2)

def run_command(remove_first_path = False):
    r"""Process the command line args and call test().

    If the '-r' option is given, the number of errors and tests is printed to
    stdout separated by a space.

    Returns an exit status of 1 if any errors are reported.
    """
    if len(sys.argv) < 2: usage()
    if sys.argv[1] == '-r':
        if len(sys.argv) != 3: usage()
        print_numbers = True
        filename = sys.argv[2]
    else:
        if len(sys.argv) != 2: usage()
        print_numbers = False
        filename = sys.argv[1]
    errors, tests = test(filename, remove_first_path)
    if print_numbers: sys.stdout.write("%d %d\n" % (errors, tests))
    if errors: sys.exit(1)

if __name__ == "__main__":
    run_command()
