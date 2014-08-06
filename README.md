tmc.py [docs](https://JuhaniImberg.github.io/tmc.py/)
=====================================================

`tmc.py` is a commandline client for working with a [TestMyCode server](https://github.com/testmycode/tmc-server). It aims to have all of the features of [tmc-netbeans](https://github.com/testmycode/tmc-netbeans).

installation
------------

Requires Python 3.3+ and pip.

    pip3 install git+https://github.com/JuhaniImberg/tmc.py.git

or

    pip3 install tmc

usage
----

[See here](https://JuhaniImberg.github.io/tmc.py/)

example
-------

    while course is not completed:
        tmc run subl3 && tmc test && tmc submit && tmc next

testing
-------

You will need to install nose. (`pip install nose`)

    TMC_PASSWORD=PUTITHERE TMC_USERNAME=PUTITHERE nosetests -v --nologcapture

more options in `testsetup.py`

license
-------

MIT, see `LICENSE`
