#!/usr/bin/python

# testdoc.py [-d] [-r] file

import sys
import os, os.path
import doctest
import warnings
from doctest_tools import setpath

debug = False

warnings.simplefilter('default')

def import_module(modulepath, remove_first_path = False, full = True):
    r"""Imports the module indicated by modulepath.

    Also adds the proper containing directories to Python's sys.path.

    Returns the imported module.
    """
    pythonpath = \
      setpath.setpath(modulepath, remove_first=remove_first_path, full=full)
    if debug:
        sys.stderr.write("setpath added: %s\n" % (pythonpath,))
    modulepath = modulepath[len(pythonpath[0]) + 1:]
    if debug:
        sys.stderr.write("modulepath: %s\n" % (modulepath,))
    modulename = modulepath.replace('/', '.').replace(os.path.sep, '.')
    if debug:
        sys.stderr.write("modulename: %s\n" % (modulename,))
    module = __import__(modulename)
    for comp in modulename.split('.')[1:]:
        module = getattr(module, comp)
    return module

def test(path, remove_first_path = False, full = True):
    r"""Runs doctest on the file indicated by 'path'.

    This will run testmod if the file ends in .py, .pyc or .pyo; and testfile
    for all other files.

    When running testfile on python 2.5, it enables Python's "with" statement
    (as if the file being tested had done "from __future__ import
    with_statement").  This is done because doing the __future__ import does
    not work in files. :-(

    Also when running testfile, the current working directory is first set to
    the directory containing the file.  This is not done for python modules
    (.py, .pyc or .pyo files).

    In all cases, all non-package directories containing package directories
    (i.e., directories containing an __init__.{py,pyc,pyo} file) are added to
    sys.path.  The search is started in the directory containing the file.  If
    the bottom-most directory is not a package directory, it is added to the
    path too.
    """
    path = os.path.normpath(path)
    fullpath = os.path.abspath(path)
    if path.endswith('.py'):
        module = import_module(fullpath[:-3], remove_first_path, full)
    elif path.endswith(('.pyc', '.pyo')):
        module = import_module(fullpath[:-4], remove_first_path, full)
    else:
        new_paths = \
          setpath.setpath(fullpath, remove_first=remove_first_path, full=full)
        if debug:
            sys.stderr.write("setpath added: %s\n" % (new_paths,))
        os.chdir(os.path.dirname(fullpath))
        if sys.version_info[:2] == (2, 5):
            import __future__
            return doctest.testfile(fullpath, False,
                                    globs={
                                      'with_statement':
                                        __future__.with_statement,
                                    })
        else:
            return doctest.testfile(fullpath, False)
    module.doing_doctest = True
    return doctest.testmod(module)

def usage():
    sys.stderr.write("usage: %s [-d] [-r] file\n"
                       "       if -d is specified, debug output is turned on\n"
                       "       if -r is specified, the number of errors "
                       "and tests is printed to stderr\n"
                     % os.path.basename(sys.argv[0]))
    sys.exit(2)

def run_command(remove_first_path = False):
    r"""Process the command line args and call test().

    If the '-r' option is given, the number of errors and tests is printed to
    stdout separated by a space.

    Returns an exit status of 1 if any errors are reported.
    """
    global debug
    print_numbers = False
    command_args = sys.argv[1:]
    if not command_args:
        usage()
    if command_args[0] in ('-h', '--help'):
        usage()
    if command_args[0] == '-d':
        if len(command_args) < 2:
            usage()
        debug = True
        del command_args[0]
    if command_args[0] == '-r':
        if len(command_args) < 2:
            usage()
        print_numbers = True
        del command_args[0]
    if len(command_args) != 1:
        usage()
    filename = command_args[0]
    try:
        errors, tests = test(filename, remove_first_path)
    except IOError:
        sys.stdout.write("%s: file not found\n\n" % filename)
        usage()
    except ImportError:
        sys.stdout.write("%s: module not found\n\n" % filename)
        usage()
    if print_numbers:
        sys.stdout.write("TESTDOC RESULTS: Errors %d, Tests %d\n" %
                           (errors, tests))
    if errors: sys.exit(1)

if __name__ == "__main__":
    run_command()
