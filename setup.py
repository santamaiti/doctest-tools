# setup.py

import sys
import os, os.path
#import glob
from distutils.core import setup
from distutils import file_util

def rm_r(dir):
    for root, dirs, files in os.walk(dir, topdown=False):
       for name in files:
           os.remove(os.path.join(root, name))
       for name in dirs:
           os.rmdir(os.path.join(root, name))
    if os.path.isdir(dir): os.rmdir(dir)

rm_r('build')
#for f in glob.glob('scripts/testdoc-*'): os.remove(f)
#for f in glob.glob('scripts/testall-*'): os.remove(f)

def scripts():
    scripts = ['scripts/testdoc', 'scripts/testall']
    if 'install' not in sys.argv[-1]: return scripts
    suffix = "%d.%d" % sys.version_info[:2]
    if sys.executable.lower().endswith('python'):
        ans = scripts[:]
    else:
        ans = []
    for oldname in scripts:
        newname = "%s-%s" % (oldname, suffix)
        file_util.copy_file(oldname, newname)
        ans.append(newname)
    #sys.stderr.write("scripts: %r\n" % ans)
    return ans

setup(
    name = "doctest-tools",
    version = "1.0a1",
    packages = ['doctest_tools'],
    scripts = scripts(),

    #zip_safe = True,

    # Metadata for upload to PyPI
    author = "Bruce Frederiksen",
    author_email = "dangyogi@gmail.com",
    description = "Tools to run doctests on code and text files within a directory",
    license = "MIT License",
    keywords = "doctest python unit test script",
    url = "http://code.google.com/p/doctest-tools",
    long_description = """
        These are a small set of tools to make it easier to run doctest on your
        source files and text files.

        There is a tool to run doctest on an individual file, and another tool
        to run doctest on all files within a directory (recursively).  The
        individual doctest runs are done in separate processes so that the
        tests don't contaminate each other.

        Finally, there is a small module to set the python path of the program
        calling it to make it easier to run the program from multiple clones of
        the same project where it is impossible to set the python path to a
        single location.

        These tools are written in Python so that they will run on all
        platforms.

        The egg files installed by easy_install are:
          - FIX ME 2.5
          - FIX ME 2.6
          - FIX ME 3.1
    """,
    download_url =
        "FIX ME",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
)

