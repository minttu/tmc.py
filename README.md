tmc.py
======

A Python2 terminal client for working with a TestMyCode server.
Note: this is still under developement and might have fatal bugs.
Tested under GNU/Linux, but might work with other platforms.

todo
====

    comment & clean code
    --verbose
    --quiet
    remove
    make next-exercise and previous-exercise check if there are more

real world usage
================

    tmc init
    tmc set-exercise k2014-mooc/viikko1/Viikko1_001.Nimi

    # untill you have completed the course
    tmc test && tmc submit && tmc next

commands
========

IDs can be the number IDs or the folder that contains a course/exercise.
You don't need to provide IDs again if you use `set-exercise` and `set-course`.

    tmc init                                     # asks for server, username and password and saves them for future usage
    tmc list-courses (or lc)                     # lists all courses
    tmc list-exercises (or ls) [CourseID]        # lists all exercises from course ID
    tmc download-exercises (or dl) [CourseID]    # downloads all exercises from course ID
    tmc update-exercises [CourseID]              # updates all exercises without overriding user code
    tmc submit-exercise (or submit) [ExerciseID] # submits a exercise for testing
    tmc test-exercise (or test) [ExerciseID]     # tests exercise locally

    tmc set-course [CourseID]                  # sets the default CourseID, so that you don't need to write it again
    tmc unset-course                           # resets the default CourseID

    tmc set-exercise ID                        # sets the default ExerciseID
    tmc unset-exercise                         # resets the default ExerciseID
    tmc next-exercise (or next)                # goes to the next exercise
    tmc previous-exercise (or prev)            # goes to the previous exercise

    tmc submission [SubmissionID]              # get info from submission

    tmc help [command]


installation
============

    get python2.7
    get pip
    optionally also get apache-ant for local tests
    (sudo) pip install tmc

license
=======

MIT, see `LICENSE`