tmc.py
======

A Python2 terminal client for working with a TestMyCode server.
Note: this is still under developement and might have fatal bugs.
Tested under GNU/Linux, but might work with other platforms.

todo
====

    handle changing directories better (currently you need to do everything in the same dir as tmc.py is)
    comment code
    --verbose
    --quiet
    remove
    make next-exercise and previous-exercise check if there are more
    clean code

real world usage
================

    ./tmc.py init
    ./tmc.py set-course 18
    ./tmc.py download-exercises
    ./tmc.py set-exercise k2014-mooc/viikko1/Viikko1_001.Nimi

    # untill you have completed the course
    ./tmc.py test-exercise && ./tmc.py submit-exercise && ./tmc.py next-exercise

commands
========

IDs can be the number IDs or the folder that contains a course/exercise.
You don't need to provide IDs again if you use `set-exercise` and `set-course`.

    ./tmc.py init                                   # asks for server, username and password and saves them for future usage
    ./tmc.py list-courses                           # lists all courses
    ./tmc.py list-exercises [ID]                    # lists all exercises from course ID
    ./tmc.py download-exercises [ID]                # downloads all exercises from course ID
    ./tmc.py update-exercises [ID]                  # updates all exercises without overriding user code
    ./tmc.py submit-exercise [ExerciseID][CourseID] # submits a exercise for testing
    ./tmc.py test-exercise [ExerciseID][CourseID]   # tests exercise locally

    ./tmc.py set-course [ID]                        # sets the default CourseID, so that you don't need to write it again
    ./tmc.py unset-course                           # resets the default CourseID

    ./tmc.py set-exercise ID                        # sets the default ExerciseID
    ./tmc.py unset-exercise                         # resets the default ExerciseID
    ./tmc.py next-exercise                          # goes to the next exercise
    ./tmc.py previous-exercise                      # goes to the previous exercise

    ./tmc.py submission [ID]                        # get info from submission

    ./tmc.py help [command]


installation
============

    get python2.7
    get pip
    optionally also get apache-ant for local tests
    (sudo) pip install tmc

license
=======

MIT, see `LICENSE`