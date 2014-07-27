tmc.py
======

This is a complete redo of tmc.py targeting exclusively Python3. It's not usable
yet, but it tries to have a little bit nicer structure.

note
----

The legacy branch has the python2 version. It's the version also in [PyPi](https://pypi.python.org/pypi/tmc/0.2.2)

todo
----

* Testing script

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

usage
----

### `tmc configure`

Set the server, user credentials and selected course.

### `tmc select [--course]`

Selects a exercise. If `--course` is given selects a course instead.

### `tmc update [--course]`

Update the list of exercises. If `--course` is given updates courses instead.

### `tmc download [all|id]`

Download all of the exercises or a exercise with the id.

### `tmc test [id]`

Test the current exercise or a exercise with the id.

### `tmc submit [id] [--paste] [--review]`

Submit the current exercise or a exercise with the id. If `--paste` is set the submission will be sent to TMC pastebin. If `--review` is set a request for review will be created.

### `tmc next`

Go to the next exercise.

### `tmc run command`

Executes `command exercise-path`. For example `tmc run gvim` would run
`gvim /home/x/tmc/k2014-algomooc/viikko1/01.1.Kertoma` which would open gvim
in that folder.

### `tmc reset`

Reset the database.



example
-------

    while course is not completed:
        tmc run subl3 && tmc test && tmc submit && tmc next

license
-------

MIT, see `LICENSE`
