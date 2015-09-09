#!/usr/bin/env python3

from setuptools import setup
import os
import sys

if sys.version_info < (3, 2, 0):
    raise Exception("Only python 3.2+ is supported.")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exec(read('tmc/version.py'))

setup(
    name='tmc',
    version=__version__,
    description='TestMyCode client',
    long_description=read("README.rst"),
    author='Juhani Imberg',
    author_email='juhani@imberg.com',
    url='http://github.com/JuhaniImberg/tmc.py/',
    license='MIT',
    packages=['tmc', 'tmc.exercise_tests', 'tmc.tests', 'tmc.ui'],
    entry_points={
        'console_scripts': [
            'tmc = tmc.__main__:main',
            'tmc3 = tmc.__main__:main'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ],
    install_requires=[
        "requests == 2.7.0",
        "argh == 0.26.1",
        "peewee == 2.6.3"
    ],
)
