# setpath.py

import os.path
import sys

def pkg(path):
    for suffix in 'py', 'pyc', 'pyo':
        if os.path.exists(os.path.join(path, '__init__.' + suffix)):
            return True
    return False

def setpath(filepath = None, remove_cwd = True, remove_first = True):
    filepath = os.path.abspath(filepath)
    if not os.path.isdir(filepath): filepath = os.path.split(filepath)[0]
    while pkg(filepath): filepath = os.path.split(filepath)[0]
    if remove_first: del sys.path[0]       # kill path to this program...
    if remove_cwd and '' in sys.path: sys.path.remove('')
    if filepath in sys.path: sys.path.remove(filepath)
    sys.path.insert(0, filepath)
    return filepath

