These are a small set of tools to make it easier to run doctest on your source files and text files.

There is a tool to run doctest on an individual file, and another tool to run doctest on all files within a directory (recursively).  The individual doctest runs are done in separate processes so that the tests don't contaminate each other.

Finally, there is a small module to set the python path of the program calling it to make it easier to run the program from multiple clones of the same project where it is impossible to set the python path to a single location.

These tools are written in Python so that they will run on all platforms with Python 2.5 through Python 3.