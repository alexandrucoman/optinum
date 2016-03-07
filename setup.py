#! /usr/bin/env python
# *-* encoding: UTF-8 *-*
"""
Setup script for the optinum package.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="optinum",
    version="0.1a",
    description=(
        "This project provides the user with an analysis regarding "
        "the results obtained by a couple of algorithms."),
    long_description=open("README.md").read(),
    author=("Alexandru Coman, Alexandru Cîtea"),
    author_email=("Alexandru Coman <contact@alexcoman.com>, "
                  "Alexandru Cîtea <alex@citea.ro>"),
    url="https://github.com/c-square/optinum",
    packages=["optinum"],
    scripts=["scripts/optinum"],
    requires=open("requirements.txt").readlines()
)
