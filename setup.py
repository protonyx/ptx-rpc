"""
Setuptools build file

:author: KKENNEDY
"""

# Version (Semantic Versioning)
VER_MAJOR = 0
VER_MINOR = 1
VER_PATCH = 0

# Is this a release version? If so, additional data is appended to full version
RELEASE = False

# Release type
REL_TYPE = 'dev0'    # Development Release
# REL_TYPE = 'alpha0' # Alpha Release
# REL_TYPE = 'beta0'  # Beta Release
# REL_TYPE = 'rc1'    # Release Candidate

# -----------------------------------------------------------------------
# DO NOT CHANGE ANYTHING BELOW THIS LINE
# -----------------------------------------------------------------------

VERSION = '%d.%d.%d' % (VER_MAJOR, VER_MINOR, VER_PATCH)

import os
import sys
import time
from setuptools import find_packages

def build_package():

    # Setup Metadata
    setup_meta = dict(
        # Application name:
        name='PTX-RPC',

        # Version number
        version=VERSION,

        # Application author details:
        author="Kevin Kennedy",
        author_email="protonyx@users.noreply.github.com",

        license="MIT",

        # Packages
        packages=['rpc'],

        # Package data - e.g. non-python modules
        #package_data = {},
        # Include additional files into the package
        include_package_data=True,

        # Details
        url="https://github.com/protonyx/ptx-rpc",

        #
        # license="LICENSE.txt",
        description='PTX-RPC',

        # Platforms
        platforms=["Windows", "Mac OS-X", "Linux"],

        # long_description=open("README.txt").read(),

        # Dependent packages (distributions)
        install_requires=[
            #"jsonlib2",
            "pyvisa",
            "pyserial",
            "numpy",
            "matplotlib",
        ],

        # Unit tests
        test_suite="tests.test_suite"
    )

    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

    # Setuptools
    setup(**setup_meta)

if __name__ == '__main__':
    build_package()