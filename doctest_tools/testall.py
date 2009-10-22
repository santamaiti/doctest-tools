#!/usr/bin/python

# testall.py [py | tst | txt]

import os, os.path
import sys
import subprocess
import traceback

def execute(args, print_last_line = True):
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
    return lines[-1] if lines else None

def call_testdoc(path):
    if sys.version_info[0] == 2 and sys.version_info[1] >= 6:
        last_line = execute((sys.executable, '-3', '-S',
                               '-m', 'doctest_tools.testdoc', '-r', path),
                            False)
    else:
        last_line = execute((sys.executable,
                               '-m', 'doctest_tools.testdoc', '-r', path),
                            False)

    if last_line:
        try:
            return tuple(int(x) for x in last_line.split())
        except ValueError:
            sys.stdout.write(last_line + '\n')
    return 1, 0

def run(*suffixes):
    #sys.stdout.write("run %r\n" % suffixes)
    if not suffixes: suffixes = 'py', 'tst', 'txt'
    suffixes = tuple((s if s[0] == '.' else '.' + s) for s in suffixes)

    errors = 0
    tests = 0
    files = 0

    for dirpath, dirnames, filenames in os.walk('.'):
        if '.hg' in dirnames: dirnames.remove('.hg')
        if '.svn' in dirnames: dirnames.remove('.svn')
        if 'build' in dirnames: dirnames.remove('build')
        if 'dist' in dirnames: dirnames.remove('dist')
        for filename in filenames:
            if filename.startswith('setup') and filename.endswith('.py'):
                continue
            path = os.path.join(dirpath, filename)
            if any(map(lambda suffix: filename.endswith(suffix), suffixes)):
                sys.stdout.write("Testing %s\n" % path)
                files += 1
                try:
                    e, t = call_testdoc(os.path.abspath(path))
                except Exception:
                    e, t = 1, 0
                    traceback.print_exc()
            else:
                e = t = 0
            errors += e
            tests += t
    return files, tests, errors


def usage():
    sys.stderr.write("usage: testall.py [py | tst | txt]...\n")
    sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'): usage()
    files, tests, errors = run(*sys.argv[1:])
    sys.stdout.write("Files: %d, Tests: %d, Errors: %d\n" %
                       (files, tests, errors))
    if errors: sys.exit(1)
