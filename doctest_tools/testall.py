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

    Returns the last_line (or None if no output), process return code
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
    base, ext = os.path.splitext(filename)
    return ext, base

def run(suffixes, py3kwarning = False):
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
