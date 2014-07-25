tmc.py
======

This is a complete redo of tmc.py targeting exclusively Python3. It's not usable
yet, but it tries to have a little bit nicer structure.

todo
====

* Start using a ORM for the dirty DB work.

state
=====

Works

* Login
* Downloading
* Testing with ant
* Submitting

Needs Polish

* All

example
=======

    while course is not completed:
        tmc run subl3 && tmc test && tmc submit && tmc next

license
=======

MIT, see `LICENSE`
