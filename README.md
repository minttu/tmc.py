tmc.py
======

`tmc.py` is a commandline client for working with a [TestMyCode server](https://github.com/testmycode/tmc-server). It aims to have all of the features of [tmc-netbeans](https://github.com/testmycode/tmc-netbeans).

note
----

The legacy branch has the python2 version. It's the version also in [PyPi](https://pypi.python.org/pypi/tmc/0.2.2)

installation
------------

    Requires Python 3.3+ and pip
    pip3 install git+https://github.com/JuhaniImberg/tmc.py.git

usage
----

[See here](https://JuhaniImberg.github.io/tmc.py/)

example
-------

    while course is not completed:
        tmc run subl3 && tmc test && tmc submit && tmc next

state
-----

Works

* Login
* Downloading
* Testing with ant
* Submitting

Needs Polish

* All

ToDo

* More docs
* Testing script

license
-------

MIT, see `LICENSE`
