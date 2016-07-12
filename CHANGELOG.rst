Changelog
=========

1.0.1
-----

* Handle invalid UTF-8 more gracefully

1.0.0
-----

* Uses server generated URLs for submitting and everything else except the
  initial ``courses.json``
* Database schema migration system

0.3.18
------

* Fixed running GTest when there were `c` files in the `src` directory.

0.3.17
-----

* Fixed path to exercise resolving (#31)

0.3.16
------

* C++/gtest support


0.3.15
------

* Valgrind support

0.3.14
------

* Bugfixes

0.3.13
------

* Refactoring
* C compiler warnings are shown

0.3.10 - 0.3.12
---------------

* Bugfix

0.3.9
-----

* C compile failures work
* XML escaping workaround is more gentle

0.3.8
-----

* Test updating is back with ``tmc update`` or ``tmc download --update``
* Possible workaround for XML escaping

0.3.7
-----

* Should work on Windows better
* Cleaner exercise tests

0.3.6
-----

* Added ``tmc.ini`` file with:
    * Toggle colors
    * Toggle unicode characters
    * Show successful tests
* Added a weekly check for updates to ``tmc.py``
* Fixes

0.3.5
-----

* Added ``--auto`` to ``tmc configure``
* Directory sensitive testing and submitting
* More information in several places
