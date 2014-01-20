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

def list_courses():
    conf = config.Config()
    conf.load()

    conn = connection.Connection(conf.server, conf.auth)
    Pretty.list_courses(conn.get_courses())

def list_exercises(course_id):
    conf = config.Config()
    conf.load()

    conn = connection.Connection(conf.server, conf.auth)
    Pretty.list_exercises(conn.get_course(int(course_id)).exercises)

def download_exercises(course_id):
    conf = config.Config()
    conf.load()

    conn = connection.Connection(conf.server, conf.auth)
    conn.download_exercises(conn.get_course(int(course_id)).exercises)

def submit_exercise(course_id, exercise_id):
    conf = config.Config()
    conf.load()

    conn = connection.Connection(conf.server, conf.auth)
    conn.submit_exercise(conn.get_exercise(int(course_id), int(exercise_id)), Pretty.print_submission)

def main():
    parser = argh.ArghParser()
    parser.add_commands([init, list_courses, list_exercises, download_exercises, submit_exercise])
    parser.dispatch()