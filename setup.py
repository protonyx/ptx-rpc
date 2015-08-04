"""
Setuptools build file

:author: KKENNEDY
"""

# Version (Semantic Versioning)
VER_MAJOR = 0
VER_MINOR = 9
VER_PATCH = 1

# Is this a release version? If so, additional data is appended to full version
RELEASE = True

# Release type
# REL_TYPE = 'dev0'    # Development Release
REL_TYPE = 'alpha0' # Alpha Release
# REL_TYPE = 'beta0'  # Beta Release
# REL_TYPE = 'rc1'    # Release Candidate

# -----------------------------------------------------------------------
# DO NOT CHANGE ANYTHING BELOW THIS LINE
# -----------------------------------------------------------------------

VERSION = '%d.%d.%d' % (VER_MAJOR, VER_MINOR, VER_PATCH)

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

        # License
        license="MIT",

        # Details
        url="https://github.com/protonyx/ptx-rpc",

        # Description
        description='Asymmetric Python RPC Library with a REST API and JSON-RPC transport',

        # Long Description
        long_description=open("readme.rst").read(),

        # Keywords
        keywords='RPC,JSON-RPC',

        # Classifiers
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Operating System :: MacOS :: MacOS X",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ],

        # Platforms
        platforms=["Windows", "Mac OS-X", "Linux"],

        # Packages
        packages=['ptxrpc'],

        # Package data - e.g. non-python modules
        #package_data = {},
        # Include additional files into the package
        include_package_data=True,

        # Dependent packages (distributions)
        install_requires=[
            #"jsonlib2",
            "requests",
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