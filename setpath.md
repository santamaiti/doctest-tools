# setpath #

The setpath module is used to add the current project directory to Python's `sys.path`.

## rationale ##

Sometimes you have several copies of the same project that you are working on.  Maybe even have the project installed in the Python site-packages directory and also a source directory for development work.  Or maybe multiple source directories, for example, when using a distributed version control system such as mercurial.

You may also want to be able to run modules from different subdirectories within the project directory and have them all use the same parent project directory on the Python path.

In these cases, hard-coding the project directory on the Python path won't work.  These are the problems that setpath solves.

## terminology: package directory ##

A "package directory" is defined by Python as a directory containing any of the files: `__init__.py`, `__init__.pyc`, and/or `__init__.pyo`.


## usage ##

Before importing any modules from the project, all you need to do is:

```
from doctest_tools import setpath
setpath.setpath(__file__)
```

This proceeds up the directory structure looking for directories that have package directories as direct subdirectories, but are not package directories themselves.  These directories are added to the front of `sys.path` and returned from setpath as a list.

If the bottom-most directory is not a package directory, it is also added to `sys.path`.

By default, only the first directory found is added to `sys.path` and returned (as a list with one name in it).  But you can also specify that all matching directories be added to `sys.path` and returned.

## options ##

The setpath function takes three options:

```
def setpath(filepath, remove_cwd = True, remove_first = False, full = False)
```

The `remove_cwd` option removes an '' entry (if any) from sys.path.

The `remove_first` option removes the first entry from sys.path (regardless of what it is).

`remove_first` is used when called from a script.  When the script is run as "python somewhere/foobar.py" (or as a script with "#!/usr/bin/python"), python adds the directory containing foobar.py to `sys.path`.  The `remove_first` option undoes this (albeit blindly -- it doesn't do any sanity checks first).  But note that python does _not_ add anything to `sys.path` when called with the '-m' option, for example: "python -m somewhere.foobar".  In this case, "somewhere" must have been on the python path to begin with for python to even find it in the first place...

The `full` option causes all matching directories to be added to `sys.path` and returned if set to `True`.  Otherwise, only the first matching directory is added to `sys.path` and returned.

## other useful functions ##

### is\_package ###

```
def is_package(path)
```

Returns True if `path` is a package directory.

### has\_package ###

```
def has_package(path)
```

Returns True if `path` has a package directory as a direct subdirectory.  It does not matter to has\_package whether `path` itself is a package directory or not.

### find\_roots ###

```
def find_roots(dirpath)
```

This is a generator for directories to add to `sys.path`.  It yields the full absolute path of each directory to be added (but does not add it to `sys.path` itself).

`dirpath` may be either the path to a file or directory.  If it is the path to a file, the directory containing that file is used as the starting point.