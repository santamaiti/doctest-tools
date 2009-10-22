# setup.py

from distutils.core import setup

setup(
    name = "doctest-tools",
    version = "1.0a1",
    packages = ['doctest_tools'],
    scripts = ['doctest_tools/testdoc.py', 'doctest_tools/testall.py'],
    #data_files = [('pyke', ['copyright_license', 'hgrc_keywords', 'README'])],

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

