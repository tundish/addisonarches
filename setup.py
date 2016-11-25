#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # May include bzr revsion number
    from addisonarches.about import version
except ImportError:
    try:
        # For setup.py install
        from addisonarches import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(
                    open(os.path.join(os.path.dirname(__file__),
                    "addisonarches", "__init__.py"),
                    'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="addisonarches",
    version=version,
    description="A trading game.",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://pypi.python.org/pypi/addisonarches",
    long_description=__doc__,
    classifiers=[
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        " or later (AGPLv3+)"
    ],
    packages=[
        "addisonarches",
        "addisonarches.test",
        "addisonarches.scenario",
        "addisonarches.sequences",
        "addisonarches.sequences.test",
        "addisonarches.sequences.stripeyhole",
        "addisonarches.web",
    ],
    package_data={
        "addisonarches": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
        ],
        "addisonarches.web": [
            "static/audio/*.wav",
            "static/css/*.css",
            "static/css/*/*.css",
            "static/fonts/*.ttf",
            "static/fonts/*.woff",
            "static/img/*.jpg",
            "static/img/*.png",
            "static/js/*.js",
            "static/rson/*.rson",
            "templates/*.prt",
            "templates/*.tpl",
        ],
        "addisonarches.sequences.stripeyhole": [
            "*.rst",
        ]
    },
    install_requires=[
        "aiohttp>=0.17.4",
        "rson>=0.9",
        "pyratemp>=0.3.2",
        "tallywallet-common>=0.009.0",
        "turberfield-dialogue>=0.3.0",
        "turberfield-ipc>=0.13.0",
        "turberfield-utils>=0.21.0",
    ],
    extras_require={
        "dev": [
            "pep8>=1.6.2",
        ],
        "docbuild": [
            "babel>=2.2.0",
            "sphinx-argparse>=0.1.15",
            "sphinxcontrib-seqdiag>=0.8.4",
        ],
    },
    tests_require=[
    ],
    entry_points={
        "console_scripts": [
            "addisonarches = addisonarches.main:run",
            "addisonarches-web = addisonarches.web.main:run",
        ],
        "turberfield.interfaces.sequence": [
            "stripeyhole = addisonarches.sequences.stripeyhole:contents",
        ],
        "turberfield.interfaces.ensemble": [
            "sequence_01 = addisonarches.scenario.common:ensemble",
        ],
    },
    zip_safe=False
)
