tmc.py `docs`_
==============

``tmc.py`` is a commandline client for working with a `TestMyCode
server`_. It aims to have all of the features of `tmc-netbeans`_.

installation
------------

Requires Python 3.2+ and pip.

::

    pip3 install git+https://github.com/JuhaniImberg/tmc.py.git

or

::

    pip3 install tmc

usage
-----

`See here`_

example
-------

::

    while course is not completed:
        tmc run subl3 && tmc test && tmc submit && tmc next

testing
-------

You will need to install nose. (``pip install nose``)

::

    TMC_PASSWORD=PUTITHERE TMC_USERNAME=PUTITHERE nosetests -v --nologcapture

more options in ``testsetup.py``

license
-------

MIT, see ``LICENSE``

.. _docs: https://JuhaniImberg.github.io/tmc.py/
.. _TestMyCode server: https://github.com/testmycode/tmc-server
.. _tmc-netbeans: https://github.com/testmycode/tmc-netbeans
.. _See here: https://JuhaniImberg.github.io/tmc.py/
