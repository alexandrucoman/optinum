#! /usr/bin/env python
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
    author=("Alexandru Coman"),
    author_email=("Alexandru Coman <alex@ropython.org>"),
    url="https://github.com/alexandrucoman/optinum",
    packages=["optinum"],
    scripts=["scripts/optinum"],
    requires=[]
)
