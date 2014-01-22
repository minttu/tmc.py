#!/usr/bin/env python2

from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='tmc',
    version='0.1',
    description='TestMyCode client',
    author='Juhani Imberg',
    author_email='juhani@imberg.com',
    url='http://github.com/JuhaniImberg/tmc.py/',
    license='MIT',
    scripts=['bin/tmc'],
    packages=['tmc'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "requests >= 2.2.0",
        "python-dateutil >= 2.2",
        "pytz >= 2013.9",
        "argh >= 0.23.3",
    ],
)