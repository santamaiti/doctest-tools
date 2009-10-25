# setpath.py

import os.path
import sys

def is_package(path):
    for suffix in 'py', 'pyc', 'pyo':
        if os.path.exists(os.path.join(path, '__init__.' + suffix)):
            return True
    return False

def setpath(filepath = None, remove_cwd = True, remove_first = False):
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

