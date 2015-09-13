tmc.py `docs`_
==============

``tmc.py`` is a commandline client for working with a `TestMyCode
server`_. It aims to have all of the features of `tmc-netbeans`_.

installation
------------

Requires ``Python 3.2`` + and ``pip`` / ``virtualenv``. If you have root access

::

    sudo pip3 install tmc

otherwise

::

    curl -L https://rawgit.com/JuhaniImberg/tmc.py/master/tmcpy-inst.sh | bash

If you are running a Windows OS, please install `curses`_ for Python.

If you want to try out the git version you can do so by cloning this repository,
activating your virtualenv and ``./setup.py install``.

tutorial / usage
----------------

`See here`_

version numbers
---------------

`SemVer`_ will be adopted starting with the 1.0.0 release.

license
-------

MIT, see ``LICENSE``

.. _docs: https://JuhaniImberg.github.io/tmc.py/
.. _TestMyCode server: https://github.com/testmycode/tmc-server
.. _tmc-netbeans: https://github.com/testmycode/tmc-netbeans
.. _See here: https://JuhaniImberg.github.io/tmc.py/tutorial.html
.. _curses: http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
.. _SemVer: http://semver.org/
