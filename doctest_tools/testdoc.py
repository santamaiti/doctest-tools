#!/usr/bin/python

# testdoc.py [-r] file

import warnings
import os, os.path
import sys
import doctest
from doctest_tools import setpath

warnings.simplefilter('default')

def import_module(modulepath, remove_first_path = False):
    pythonpath = setpath.setpath(modulepath, remove_first=remove_first_path)
    #sys.stdout.write("setpath: %s\n" % pythonpath)
    modulepath = modulepath[len(pythonpath) + 1:]
    modulename = modulepath.replace('/', '.').replace(os.path.sep, '.')
    module = __import__(modulename)
    for comp in modulename.split('.')[1:]:
        module = getattr(module, comp)
    return module

def test(path, remove_first_path = False):
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
        return doctest.testfile(fullpath, False)
    module.doing_doctest = True
    return doctest.testmod(module)

def usage():
    sys.stderr.write("usage: %s [-r] file\n" % os.path.basename(sys.argv[0]))
    sys.exit(2)

def run_command(remove_first_path = False):
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
