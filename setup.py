#!/usr/bin/env python3
"""
Module Description:
--------------------------------------------------------------------------------    
A script used to install the pyradarlib package on the local machine 
--------------------------------------------------------------------------------

"""
__author__ = 'Stephen Horst'
__author_email__ = 'sjhorst@radixpoint.org'

from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
import os
import sys
import subprocess
import re

# Used for Cython
# from numpy import get_include

try:
    __full_version__ = subprocess.check_output(['git', 'describe']).decode('utf-8').rstrip()
except OSError:
    print('WARNING: The install shell is not Git Aware!!')
    __full_version__ = 'Not Available'

subcheck = re.match('^.+?(?=-)', __full_version__)
if subcheck:
    __version__ = subcheck.group(0)
else:
    __version__ = __full_version__
with open('pynance/version', 'w') as fid:
    fid.write(__full_version__)

setup(
    name="photo",
    version=__version__,
    description="Command line photo management tool",
    url='http://radixpoint.org/git/pynance',
    author=__author__,
    author_email=__author_email__,
    license='',
    keywords='',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Topic :: Financial",
        "Programming Language :: Python :: 3.4",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux"
    ],

    #package_dir = {'' : 'src'},
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["scripts", "tests", "config", "doc"]),

    # Define CLI scripts
    entry_points={'console_scripts': ['photo=photo.cli:main_entry',
        ]},

    # Install ancillary configuration files
    package_data = {'photo' : ['version', 'data/*']},

    # Unit test dependencies
    tests_require = ['pytest'],

    # Installation Dependencies
    install_requires = [],

)
