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
    Pretty.list_courses(conn.get_courses())

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
    Pretty.list_exercises(conn.get_course(int(courseid)).exercises)

@argh.decorators.arg('courseid', nargs="*", default=-1)
def download_exercises(courseid):
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
    conn.download_exercises(conn.get_course(int(courseid)).exercises)

@argh.decorators.arg('courseid', nargs="*", default=-1)
def submit_exercise(exercise_id, courseid):
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
    conn.submit_exercise(conn.get_exercise(int(courseid), int(exercise_id)), Pretty.print_submission)

def set_course(courseid):
    conf = config.Config()
    conf.load()
    conf.set_course(courseid)

def unset_course():
    conf = config.Config()
    conf.load()
    conf.unset_course()

def main():
    parser = argh.ArghParser()
    parser.add_commands([init, list_courses, list_exercises, download_exercises, submit_exercise, set_course, unset_course])
    parser.dispatch()