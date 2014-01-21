# -*- coding: utf-8 -*-

# tmccli / tmc.py
# ===============
# 
# Provides the CLI trough argh.
# 
# Copyright 2014 Juhani Imberg

import argh
from vlog import VLog as v
from config import Config
import connection
from pretty import Pretty
import os

def init():
    conf = Config()
    conf.create_new()
    v.log(0, "You can set your default course ID with \"tmc set-course ID\"")

def list_courses():
    conf = Config()
    conf.load()

    conn = connection.Connection(conf.server, conf.auth)
    Pretty.list_courses(conf.default_course, conn.get_courses())

@argh.decorators.arg("course", nargs="*", default="-1")
def list_exercises(course):
    conf = Config()
    conf.load()

    if type(course) is list:
        course = course[0]

    try:
        value = int(course)
        course = value
    except ValueError:
        course = Config.get_course_id(course)
        if course is None:
            v.log(-1, "If you really want to provide me a string, atleast point it to a course folder!")
            exit(-1)

    if course == -1:
        if conf.default_course != -1:
            course = int(conf.default_course)
            v.log(0, "Using course ID %d. (You can reset this with unset-course)" % course)
        else:
            v.log(-1, "You need to supply a course ID or save one with set-course!")
            return

    conn = connection.Connection(conf.server, conf.auth)
    Pretty.list_exercises(conf.default_exercise, conn.get_course(int(course)).exercises)

@argh.decorators.arg("course", nargs="*", default="-1")
@argh.decorators.arg("-f", "--force", help="force downloading exercises ontop of old exercises", default=False)
def download_exercises(course, *args, **kwargs):
    conf = Config()
    conf.load()

    if type(course) is list:
        course = course[0]

    try:
        value = int(course)
        course = value
    except ValueError:
        course = Config.get_course_id(course)
        if course is None:
            v.log(-1, "If you really want to provide me a string, atleast point it to a course folder!")
            exit(-1)

    if course == -1:
        if conf.default_course != -1:
            course = int(conf.default_course)
            v.log(0, "Using course ID %d. (You can reset this with unset-course)" % course)
        else:
            v.log(-1, "You need to supply a course ID or save one with set-course!")
            return

    conn = connection.Connection(conf.server, conf.auth)
    conn.force = kwargs["force"]
    conn.download_exercises(conn.get_course(int(course)).exercises)

@argh.decorators.arg("exercise", nargs="*", default="-1")
@argh.decorators.arg("course", nargs="*", default="-1")
@argh.decorators.arg("-p", "--paste", help="make submission a paste", default=False)
@argh.decorators.arg("-r", "--review", help="request review", default=False)
@argh.decorators.arg("-t", "--trace", help="print strack trace if needed", default=False)
def submit_exercise(exercise, course, *args, **kwargs):
    conf = Config()
    conf.load()

    if type(exercise) is list:
        exercisetmp = exercise[0]
        if len(exercise) > 1:
            course = exercise[1] # oh my god please don't
        else:
            course = None
        exercise = exercisetmp

    if course is None:
            course = Config.get_course_id(exercise)
            if course is None:
                if conf.default_course != -1:
                    course = int(conf.default_course)
                    v.log(0, "Using course ID %d. (You can reset this with unset-course)" % course)
                else:
                    v.log(-1, "If you really want to provide me a string, atleast point it to a exercise folder!")
                    exit(-1)
    else:
        try:
            value = int(course)
            course = value
        except ValueError:
            course = Config.get_course_id(course)
            if course is None:
                v.log(-1, "If you really want to provide me a string, atleast point it to a course folder!")
                exit(-1)

    try:
        value = int(exercise)
        exercise = value
    except ValueError:
        exercise = Config.get_exercise_id(exercise)
        if exercise is None:
            v.log(-1, "If you really want to provide me a string, atleast point it to a exercise folder!")
            exit(-1)

    if course == -1:
        if conf.default_course != -1:
            course = int(conf.default_course)
            v.log(0, "Using course ID %d. (You can reset this with unset-course)" % course)
        else:
            v.log(-1, "You need to supply a course ID or save one with set-course!")
            return
    if exercise == -1:
        if conf.default_exercise != -1:
            exercise = int(conf.default_exercise)
            v.log(0, "Using exercise ID %d. (You can reset this with unset-exercise)" % exercise)
        else:
            v.log(-1, "You need to supply a exercise ID or save one with set-exercise!")
            return

    Pretty.trace = kwargs["trace"]
    conn = connection.Connection(conf.server, conf.auth)
    conn.paste = kwargs["paste"]
    conn.review = kwargs["review"]
    conn.submit_exercise(conn.get_exercise(int(course), int(exercise)), Pretty.print_submission)

def set_course(course):
    conf = Config()
    conf.load()

    try:
        value = int(course)
        course = value
    except ValueError:
        course = Config.get_course_id(course)
        if course is None:
            v.log(-1, "If you really want to provide me a string, atleast point it to a course folder!")
            exit(-1)

    conf.set_course(course)

def unset_course():
    conf = Config()
    conf.load()
    conf.unset_course()

def set_exercise(exercise):
    conf = Config()
    conf.load()

    try:
        value = int(exercise)
        exercise = value
    except ValueError:
        exercise = Config.get_exercise_id(exercise)
        if exercise is None:
            v.log(-1, "If you really want to provide me a string, atleast point it to a exercise folder!")
            exit(-1)

    conf.set_exercise(exercise)

def unset_exercise():
    conf = Config()
    conf.load()
    conf.unset_exercise()

def next_exercise():
    conf = Config()
    conf.load()
    conf.next_exercise()

def previous_exercise():
    conf = Config()
    conf.load()
    conf.previous_exercise()

@argh.decorators.arg("submissionid", nargs="*", default=-1, help="what submission to display, will use last submissions id if none is provided")
@argh.decorators.arg("-t", "--trace", help="print strack trace if needed", default=False)
def submission(submissionid, *args, **kwargs):
    conf = Config()
    conf.load()

    if type(submissionid) is list:
        submissionid = int(submissionid[0])

    if submissionid == -1:
        lastsub = Config.last_submission()
        if lastsub is not None:
            submissionid = int(lastsub)
            v.log(0, "Using last submissions ID")
        else:
            v.log(-1, "You need to provide a submission ID!")
            return

    Pretty.trace = kwargs["trace"]
    conn = connection.Connection(conf.server, conf.auth)
    while conn.check_submission_url("%ssubmissions/%d.json?api_version=7" % (conn.server, int(submissionid)), Pretty.print_submission) == "processing":
        time.sleep(1)

def main():
    parser = argh.ArghParser()
    parser.add_commands([init, list_courses, list_exercises, download_exercises, submit_exercise, set_course, unset_course, set_exercise, unset_exercise, next_exercise, previous_exercise, submission])
    parser.dispatch()