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

#### `tmc configure`

Set the server, user credentials and selected course.

#### `tmc select [--course] [--id x]`

Selects a exercise. If `--course` is given selects a course instead. If `--id` is given it tries to select that ID straight, without opening the curses menu.

#### `tmc update [--course]`

Update the list of exercises. If `--course` is given updates courses instead.

#### `tmc download [remaining|all|id]`

Download all of the remaining exercises that have not been completed, all of the exercises or a exercise with the id. Defaults to remaining.

#### `tmc test [id]`

Test the current exercise or a exercise with the id.

#### `tmc submit [id] [--paste] [--review]`

Submit the current exercise or a exercise with the id. If `--paste` is set the submission will be sent to TMC pastebin. If `--review` is set a request for review will be created.

#### `tmc next`

Go to the next exercise.

#### `tmc run command`

Executes `command exercise-path`. For example `tmc run gvim` would run
`gvim /home/x/tmc/k2014-algomooc/viikko1/01.1.Kertoma` which would open gvim
in that folder.

#### `tmc reset`

Reset the database.

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
