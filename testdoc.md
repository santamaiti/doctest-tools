# testdoc.py #

This command runs doctest on any file.  If the file ends in '.py', '.pyc' or '.pyo' `doctest.testmod` will be used.  Otherwise `doctest.testfile` will be used.

In either case, [setpath](setpath.md) is automatically called first on the directory containing the file.

## usage ##

```
testdoc.py [-d] [-r] filename
```

The -d option turns on debug output.

The -r option causes `testdoc.py` to output the following line to stdout at the end of the test:

```
TESTDOC RESULTS: Errors <num_errors>, Tests <num_tests>
```

The program returns exit status 1 if any errors were found.

## caveats ##

  1. The setup.py script will install testdoc.py as testdoc\_XY.py where X.Y is the python version number used to install it (for example testdoc\_26.py for python 2.6).  If the command to run setup.py was simply "python", then it is also installed as "testdoc.py".
  1. As "from future ..." does not work in modules being tested by doctest in python 2.5, testdoc.py automatically adds "from future import with\_statement" for python 2.5.