# -*- coding: utf-8 -*-

# tmccli / tmc.py
# ===============
# 
# Provides the CLI trough argh.
# 
# Copyright 2014 Juhani Imberg

import argh
from vlog import VLog as v
import config
import connection
from pretty import Pretty

def init():
    conf = config.Config()
    conf.create_new()
    v.log(0, "You can set your default course ID with \"tmc set-course ID\"")

def list_courses():
    conf = config.Config()
    conf.load()

    conn = connection.Connection(conf.server, conf.auth)
    Pretty.list_courses(conf.default_course, conn.get_courses())

@argh.decorators.arg('courseid', nargs="*", default=-1)
def list_exercises(courseid):
    conf = config.Config()
    conf.load()

    if type(courseid) is int:
        courseid = int(courseid)
    elif type(courseid) is list:
        courseid = int(courseid[0])

    if courseid == -1:
        if conf.default_course != -1:
            courseid = int(conf.default_course)
            v.log(0, "Using course ID %d. (You can reset this with unset-course)" % courseid)
        else:
            v.log(-1, "You need to supply a course ID or save one with set-course!")
            return

    conn = connection.Connection(conf.server, conf.auth)
    Pretty.list_exercises(conf.default_exercise, conn.get_course(int(courseid)).exercises)

@argh.decorators.arg("courseid", nargs="*", default=-1)
@argh.decorators.arg("-f", "--force", help="force downloading exercises ontop of old exercises", default=False)
def download_exercises(courseid, *args, **kwargs):
    conf = config.Config()
    conf.load()

    if type(courseid) is int:
        courseid = int(courseid)
    elif type(courseid) is list:
        courseid = int(courseid[0])

    if courseid == -1:
        if conf.default_course != -1:
            courseid = int(conf.default_course)
            v.log(0, "Using course ID %d. (You can reset this with unset-course)" % courseid)
        else:
            v.log(-1, "You need to supply a course ID or save one with set-course!")
            return

    conn = connection.Connection(conf.server, conf.auth)
    conn.force = kwargs["force"]
    conn.download_exercises(conn.get_course(int(courseid)).exercises)

@argh.decorators.arg("exerciseid", nargs="*", default=-1)
@argh.decorators.arg("courseid", nargs="*", default=-1)
@argh.decorators.arg("-p", "--paste", help="make submission a paste", default=False)
@argh.decorators.arg("-r", "--review", help="request review", default=False)
def submit_exercise(exerciseid, courseid, *args, **kwargs):
    conf = config.Config()
    conf.load()

    if type(exerciseid) is int:
        exerciseid = int(exerciseid)
    elif type(exerciseid) is list:
        exerciseid = int(exerciseid[0])

    if type(courseid) is int:
        courseid = int(courseid)
    elif type(courseid) is list:
        courseid = int(courseid[0])

    if courseid == -1:
        if conf.default_course != -1:
            courseid = int(conf.default_course)
            v.log(0, "Using course ID %d. (You can reset this with unset-course)" % courseid)
        else:
            v.log(-1, "You need to supply a course ID or save one with set-course!")
            return
    if exerciseid == -1:
        if conf.default_exercise != -1:
            exerciseid = int(conf.default_exercise)
            v.log(0, "Using exercise ID %d. (You can reset this with unset-exercise)" % exerciseid)
        else:
            v.log(-1, "You need to supply a exercise ID or save one with set-exercise!")
            return

    conn = connection.Connection(conf.server, conf.auth)
    conn.paste = kwargs["paste"]
    conn.review = kwargs["review"]
    conn.submit_exercise(conn.get_exercise(int(courseid), int(exerciseid)), Pretty.print_submission)

def set_course(courseid):
    conf = config.Config()
    conf.load()
    conf.set_course(courseid)

def unset_course():
    conf = config.Config()
    conf.load()
    conf.unset_course()

def set_exercise(exerciseid):
    conf = config.Config()
    conf.load()
    conf.set_exercise(exerciseid)

def unset_exercise():
    conf = config.Config()
    conf.load()
    conf.unset_exercise()

def next_exercise():
    conf = config.Config()
    conf.load()
    conf.next_exercise()

def previous_exercise():
    conf = config.Config()
    conf.load()
    conf.previous_exercise()

def main():
    parser = argh.ArghParser()
    parser.add_commands([init, list_courses, list_exercises, download_exercises, submit_exercise, set_course, unset_course, set_exercise, unset_exercise, next_exercise, previous_exercise])
    parser.dispatch()