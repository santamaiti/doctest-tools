#!/usr/bin/python

# testall.py [-3] [suffix...]

import os, os.path
import sys
import subprocess
import traceback
import optparse

def execute(args, print_last_line = True):
    r"""Executes args using subprocess and prints its output.

    The output printed includes stdout and stderr.

    The last line is not printed if print_last_line is False.

    Returns a two tuple: the last_line (or None if no output), and the process
    return code.
    """
    child = subprocess.Popen(args,
                             stdin=None,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    out = child.communicate()[0]
    if not isinstance(out, str): out = out.decode()  # for python3
    #sys.stdout.write("communicate got ")
    #sys.stdout.write(repr(out))
    #sys.stdout.write(" end output\n")
    lines = out.split('\n')
    while lines and not lines[-1]: del lines[-1]
    #sys.stdout.write("lines: %r\n" % lines)
    for line in lines[:-1]: sys.stdout.write(line + '\n')
    if print_last_line: sys.stdout.write(lines[-1] + '\n')
    return (lines[-1] if lines else None), child.returncode

def call_testdoc(path, py3kwarning = True):
    r"""Calls testdoc in a subprocess.

    The version of python used to run testdoc is the same as the version of
    python running this function.

    The stdout and stderr from testdoc are written to stdout.

    The number of errors and tests is returned as a 2-tuple.

    The py3kwarning flag will turn on the '-3' option for python if python 2.6+
    is being called.  This outputs warnings about constructs that are not
    easily translated to Python 3 with the Python's 2to3 tool.  The option is
    ignored if running Python 2.5 or before, or Python 3.
    """
    if py3kwarning and sys.version_info[0] == 2 and sys.version_info[1] >= 6:
        last_line, status = execute((sys.executable, '-3',
                                       '-m', 'doctest_tools.testdoc',
                                       '-r', path),
                                    False)
    else:
        last_line, status = execute((sys.executable,
                                       '-m', 'doctest_tools.testdoc',
                                       '-r', path),
                                    False)

    if last_line:
        try:
            return tuple(int(x) for x in last_line.split())
        except ValueError:
            pass
        sys.stdout.write(last_line + '\n')
    else:
        sys.stdout.write('ERROR: testdoc failed for %r, return code %d\n' %
                           (path, status))
    return 1, 0

def filename_key(filename):
    r"""somepath.suffix => (suffix, somepath)
    
    This is only used as the 'key' function to sort.
    """
    base, ext = os.path.splitext(filename)
    return ext, base

def run(suffixes, py3kwarning = False):
    r"""Recursively look for files and run testdoc on them.

    This starts in the current working directory and recursively looks for all
    files ending in one of the 'suffixes' provided (default 'py', 'tst', and
    'txt').  It runs testdoc on each of the files found in a separate process
    (so that tests don't cross contaminate each other).

    It automatically ignores the following directories: .hg, .svn, build and
    dest.  This list is currently hard-coded...

    It also automatically ignores any file starting with 'setup' and ending
    with '.py'.  This is also currently hard-coded...

    Finally, if there is a file called 'testall.exclude' in any subdirectory,
    the file is read to get a list of names (one per line, with lines starting
    with '#' ignored).  These names can be either directory names or file
    names.  Globbing is not allowed.  All of the names listed will be ignored
    within this directory.  BUT, note that these names will _not_ be ignored
    within subdirectories!

    The order that the tests are run is:
    
      - all matching files sorted first by file extension, then by file name.
      - all subdirectories, in sorted order.

    This function returns a 4-tuple:
    
      - the number of files tested
      - the number of tests run within those files
      - the number of tests that had errors
      - a list of the paths names for the files that had errors.
    """
    #sys.stdout.write("run %r\n" % suffixes)
    if not suffixes: suffixes = 'py', 'tst', 'txt'
    suffixes = tuple((s if s[0] == '.' else '.' + s) for s in suffixes)

    errors = 0
    tests = 0
    files = 0
    error_files = []

    for dirpath, dirnames, filenames in os.walk('.'):
        if '.hg' in dirnames: dirnames.remove('.hg')
        if '.svn' in dirnames: dirnames.remove('.svn')
        if 'build' in dirnames: dirnames.remove('build')
        if 'dist' in dirnames: dirnames.remove('dist')


        if 'testall.exclude' not in filenames:
            exclude_set = frozenset()
        else:
            f = open(os.path.join(dirpath, 'testall.exclude'))
            try:
                exclude_set = \
                  frozenset(filter(lambda line: line.strip()[0] != '#',
                                   map(lambda x: x.strip(), f)))
            finally:
                f.close()

        for x in exclude_set:
            #print "checking", repr(x), "against", dirnames
            if x in dirnames:
                #print "removing dir", x
                dirnames.remove(x)

        dirnames.sort()

        for filename in sorted(filenames, key=filename_key):
            if filename.startswith('setup') and filename.endswith('.py'):
                continue
            if filename in exclude_set: continue
            path = os.path.join(dirpath, filename)[2:]
            if any(map(lambda suffix: filename.endswith(suffix), suffixes)):
                sys.stdout.write("Testing %s\n" % path)
                files += 1
                try:
                    e, t = call_testdoc(os.path.abspath(path), py3kwarning)
                except Exception:
                    e, t = 1, 0
                    traceback.print_exc()
                if e: error_files.append(path)
            else:
                e = t = 0
            errors += e
            tests += t
    return files, tests, errors, error_files


def run_command():
    r"""Process command line args and call run().

    This also prints (to stdout) a summary of the number of files, tests and
    errors encountered, along with a list of the files that had errors.

    Returns an exit status of 1 if any errors are reported.
    """
    parser = optparse.OptionParser(
               usage="usage: %s [-h|--help] [-3] [suffix...]" %
                       os.path.basename(sys.argv[0]))
    parser.add_option('-3', action='store_true', dest='py3kwarning',
                            default=False,
                            help="warn about Python 3.x incompatibilities "
                                 "that 2to3 cannot trivially fix")
    options, args = parser.parse_args()
    files, tests, errors, error_files = run(args, options.py3kwarning)
    sys.stdout.write("Files: %d, Tests: %d, Errors: %d\n" %
                       (files, tests, errors))
    if errors:
        sys.stdout.write("********** ERRORS ************* "
                         "%d files had errors:\n" % len(error_files))
        for fn in error_files:
            sys.stdout.write(fn + '\n')
        sys.exit(1)

if __name__ == "__main__":
    run_command()
