#!/usr/bin/python

# testall.py [-3] [suffix...]

import os, os.path
import sys
import subprocess
import traceback
import optparse
import fnmatch
import re

def execute(args, line_filter = None):
    r"""Executes args using subprocess and prints its output.

    The output printed includes stdout and stderr.

    If line_filter is not None, it is applied against each line.  If it
    returns None, that line is printed to stdout.  If it returns anything
    else, that line is not printed and a list of the accumulated non-None
    values is returned.

    Returns a two tuple:
        - the list of non-None results from line_filter
        - the process return code.
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
    if lines and not lines[-1]: del lines[-1]
    #sys.stdout.write("lines: %r\n" % lines)
    ans = []
    for line in lines:
        filtered = line_filter and line_filter(line)
        if filtered is None:
            sys.stdout.write(line + '\n')
        else:
            ans.append(filtered)
    return ans, child.returncode

testdoc_results_re = re.compile(r'TESTDOC RESULTS: ([0-9]+) ([0-9]+)\r?$')

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
        matches, status = execute((sys.executable, '-3',
                                     '-m', 'doctest_tools.testdoc',
                                     '-r', path),
                                  testdoc_results_re.match)
    elif sys.version_info[:2] >= (2, 5):
        matches, status = execute((sys.executable,
                                     '-m', 'doctest_tools.testdoc',
                                     '-r', path),
                                  testdoc_results_re.match)
    else:
        matches, status = execute((sys.executable,
                                     '-c',
                                     'from doctest_tools import testdoc; '
                                       'testdoc.run_command()',
                                     '-r', path),
                                  testdoc_results_re.match)

    if matches:
        try:
            return tuple(int(x) for x in matches[0].groups())
        except ValueError:
            pass
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

def read_args(dirpath, dict):
    r"""Read the testall.config file in dirpath into dict.
    """
    f = open(os.path.join(dirpath, 'testall.config'))
    try:
        for line in f:
            line = line.strip()
            if line[0] == '#': continue
            args = line.split()
            dict.setdefault(args[0], []).extend(args[1:])
    finally:
        f.close()

def include(option_stack, name, option_type = '', default = False):
    r"""Tests whether name is included by option_type in option_stack.

    Looks through option_stack for first occurance of a glob pattern matching
    name in 'exclude' + option_type or 'include' + option_type.  A hyphen is
    added to the front of option_type, unless it's ''.
    
    Returns:
        - False if name found in 'exclude' + option_type list
        - True if name found in 'include' + option_type list
        - otherwise default
    """
    #print "include", name, repr(option_type), default
    def name_matches(prefix):
        #print "name_matches", name, prefix + option_type, options
        for pattern in options.get(prefix + option_type, ()):
            #print "name_matches testing", name, pattern
            if fnmatch.fnmatch(name, pattern):
                #print "name_matches matched, returning True"
                return True
        #print "name_matches not found, returning False"
        return False
    for dirpath, options in option_stack:
        if name_matches('exclude'):
            #print "matches exclude, returning False"
            return False
        if name_matches('include'):
            #print "matches include, returning True"
            return True
    #print "no match, returning", default
    return default

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

    errors = 0
    tests = 0
    files = 0
    error_files = []
    option_stack = []

    for dirpath, dirnames, filenames in os.walk('.'):
        if '.hg' in dirnames: dirnames.remove('.hg')
        if '.svn' in dirnames: dirnames.remove('.svn')
        if 'build' in dirnames: dirnames.remove('build')
        if 'dist' in dirnames: dirnames.remove('dist')

        #print "dirpath", dirpath
        #print "option_stack before", option_stack
        if dirpath == '.':
            # list of (dirpath, [glob_pattern])
            option_stack = [('.', {'include-suffix':
                                     suffixes or ('py', 'tst', 'txt')}
                            )]
        else:
            parent = os.path.split(dirpath)[0]
            while option_stack and option_stack[0][0] != parent:
                del option_stack[0]
            assert option_stack and option_stack[0][0] == parent, \
                   "logic error in option_stack unwinding, couldn't find %r" % \
                     parent
            option_stack.insert(0, (dirpath, {}))

        if 'testall.config' in filenames:
            read_args(dirpath, option_stack[0][1])
        #print "option_stack after", option_stack

        for dir in dirnames[:]:
            if not include(option_stack, dir, default=True):
                dirnames.remove(dir)

        dirnames.sort()

        for filename in sorted(filenames, key=filename_key):
            if filename.startswith('setup') and filename.endswith('.py'):
                continue
            suffix = os.path.splitext(filename)[1]
            if suffix: suffix = suffix[1:]  # drop the leading '.'
            if include(option_stack, filename,
                           default=include(option_stack, suffix, '-suffix')):
                path = os.path.join(dirpath, filename)[2:]
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
    parser.add_option('-s', '--summary', 
                            metavar="FILENAME",
                            help="file to write summary counts and list of "
                                 "error files to (stdout)")

    options, args = parser.parse_args()

    files, tests, errors, error_files = run(args, options.py3kwarning)

    if not options.summary or options.summary == 'stdout':
        f = sys.stdout
        f.write("\n")
        do_close = False
    elif options.summary == 'stderr':
        f = sys.stderr
        do_close = False
    else:
        f = open(options.summary, 'w')
        do_close = True
    f.write("Files: %d, Tests: %d, Errors: %d\n" % (files, tests, errors))
    if errors:
        f.write("********** ERRORS ************* "
                "%d files had errors:\n" % len(error_files))
        for fn in error_files:
            f.write(fn + '\n')
    if do_close: f.close()
    if errors: sys.exit(1)

if __name__ == "__main__":
    run_command()
