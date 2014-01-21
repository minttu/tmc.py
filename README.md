tmc.py
======

A python CLI for TestMyCode.

todo
====

    handle changing directories better (currently you need to do everything in the same dir as tmc.py is)
    comment code
    --verbose
    --quiet
    --paste
    --request-review
    remove

usage
=====

    ./tmc.py init                                   # asks for server, username and password and saves them for future usage
    ./tmc.py list-courses                           # lists all courses
    ./tmc.py list-exercises ID                      # lists all exercises from course ID
    ./tmc.py download-exercises ID                  # downloads all exercises from course ID
    ./tmc.py submit-exercise ExerciseID CourseID    # submits a exercise for testing

    ./tmc.py set-course ID                          # sets the default CourseID, so that you don't need to write it again
    ./tmc.py unset-course                           # resets the default CourseID

installation
============

    get python2.7
    get pip
    pip install -r requirements.txt

license
=======

MIT, see `LICENSE`