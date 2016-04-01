# testall.py #

This command runs [testdoc](testdoc.md).py on all `.py`, `.tst`, and `.txt` files found through a recursive scan of the current directory.

[setpath](setpath.md) is automatically called first on the directory containing each file.

## usage ##

```
testall.py [-3] [-s summary_filename] [suffix...]
```

The -3 option turns on the -3 option for python2.6 to report problems that will be encountered moving to python3.x.

The -s option writes summary information into a file rather than to stdout.

'py' 'tst' and 'txt' are the default suffixes searched for.  Specifying any suffixes on the command line overrides all of these.  Do not specify the '.' in these suffixes.

The program returns exit status 1 if any errors were found.

## testall.config files ##

`testall.py` checks each directory for a `testall.config` file.  If found, options are read from this file that affect which files are selected within that directory and all of its subdirectories.

The `testall.config` file is made up of one option per line.  Lines starting with '#' and blank lines are ignored.

Each option starts with one of:

  1. `exclude`
  1. `include`
  1. `exclude-suffix`
  1. `include-suffix`

which is followed by one or more glob patterns separated by spaces.  The options are processed in this order to see if any of the patterns in that option, or any inherited option from a `testall.config` in a parent directory, match the filename (or suffix).

## caveats ##

  1. The setup.py script will install testall.py as testall\_XY.py where X.Y is the python version number used to install it (for example testall\_26.py for python 2.6).  If the command to run setup.py was simply "python", then it is also installed as "testall.py".
  1. As "from future ..." does not work in modules being tested by doctest in python 2.5, testall.py automatically adds "from future import with\_statement" for python 2.5.
  1. `testall.py` always ignores `.hg`, `.svn`, `build`, and `dist` directories.  This behavior can not be overridden with a testall.config file.
  1. The order that the files are tested within each directory is:
    1. files first, sorted first by file extension, then by filename.
    1. then directories, sorted by name.