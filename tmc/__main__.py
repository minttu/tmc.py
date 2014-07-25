#!/usr/bin/env python3

import argh
from argh.decorators import aliases, arg, wrap_errors
import getpass
import base64
import os
import sys
from functools import wraps
from subprocess import Popen, DEVNULL
from tmc.errors import *
from tmc.prompt import prompt_yn
from tmc.spinner import SpinnerDecorator
from tmc import db, api, files, menu
from tmc.models import Course, Exercise, Config

import peewee


def needs_a_course(func):
    @wraps(func)
    def inner(*args, **kwargs):
        Course.get_selected()
        return func(*args, **kwargs)
    return inner


@aliases("reset")
@wrap_errors([TMCError])
def resetdb():
    if prompt_yn("Reset database", False):
        db.reset()


@aliases("up")
@wrap_errors([TMCError])
@arg("-c", "--course", action="store_true", help="Update courses instead.")
def update(course=False):
    if course:
        @SpinnerDecorator("Done.")
        def update_course():
            for course in api.get_courses():
                old = None
                try:
                    old = Course.get(Course.tid == course["id"])
                except Course.DoesNotExist:
                    old = None
                if old:
                    continue
                Course.create(tid=course["id"],
                              name=course["name"])
        update_course()
    else:
        selected = Course.get_selected()

        @SpinnerDecorator()
        def update_exercise():
            for exercise in api.get_exercises(selected.tid):
                old = None
                try:
                    old = Exercise.get(Exercise.tid == exercise["id"])
                except Exercise.DoesNotExist:
                    old = None
                if old is not None:
                    old.name = exercise["name"]
                    #old.course = selected.id,
                    #old.is_attempted = exercise["attempted"]
                    #old.is_completed = exercise["completed"]
                    #old.deadline = exercise.get("deadline", None)
                    old.save()
                else:
                    Exercise.create(tid=exercise["id"],
                                    name=exercise["name"],
                                    course=selected.id,
                                    is_attempted=exercise["attempted"],
                                    is_completed=exercise["completed"],
                                    deadline=exercise.get("deadline", None))
        update_exercise()
        print("Done.")


@arg("-f", "--force", default=False,
     action="store_true", help="Should the download be forced.")
@aliases("dl")
@needs_a_course
@wrap_errors([TMCError])
def download(what="all", force=False):
    what = what.upper()
    selected = Course.get_selected()
    if what == "ALL":
        for exercise in selected.exercises:
            files.download_file(exercise.tid, force=force)
    else:
        files.download_file(int(what), force=force)


@aliases("te")
@needs_a_course
@wrap_errors([TMCError])
def test(what=None):
    if what is not None:
        if not files.test(int(what)):
            exit(-1)
    else:
        sel = Exercise.get_selected()
        if not sel:
            raise NoExerciseget_selected()
        files.test(sel.tid)


@arg("-p", "--pastebin", default=False, action="store_true",
     help="Should the submission be sent to TMC pastebin.")
@arg("-r", "--review", default=False, action="store_true",
     help="Request a review for this submission.")
@aliases("su")
@needs_a_course
@wrap_errors([TMCError])
def submit(what=None, pastebin=False, review=False):
    if what is not None:
        files.submit(int(what), pastebin=pastebin, request_review=review)
    else:
        sel = Exercise.get_selected()
        if not sel:
            raise NoExerciseget_selected()
        files.submit(sel.tid, pastebin=pastebin, request_review=review)


@aliases("sel")
@wrap_errors([TMCError])
@arg("-c", "--course", action="store_true", help="Select a course instead.")
def select(course=False):
    if course:
        og = None
        try:
            og = Course.get_selected()
        except NoCourseSelected:
            pass
        start_index = 0
        if og is not None:
            start_index = og.tid
        ret = menu.launch("Select a course",
                          Course.select().execute(),
                          start_index)
        if ret != -1:
            sel = Course.get(Course.tid == ret)
            sel.set_select()
            update()
            if sel.path == "":
                selpath()
            next()
            return
        else:
            print("You can select the course with `tmc select --course`")
            return
    else:
        og = None
        try:
            og = Exercise.get_selected()
        except NoExerciseSelected:
            pass
        start_index = 0
        if og is not None:
            start_index = og.tid
        sel = Course.get_selected()
        ret = menu.launch("Select a exercise",
                          Exercise.select().where(
                              Exercise.course == sel.id).execute(),
                          start_index)
        if ret != -1:
            sel = Exercise.get(Exercise.tid == ret)
            sel.set_select()
            print("Selected {}".format(sel))


@needs_a_course
@wrap_errors([TMCError])
def next():
    sel = None
    try:
        sel = Exercise.get_selected()
    except NoExerciseSelected:
        pass
    exercises = Course.get_selected().exercises
    try:
        if sel is None:
            sel = [i for i in exercises][0]
        else:
            sel = Exercise.get(Exercise.id == sel.id + 1)
    except peewee.InterfaceError as e:
        # OK. This looks bizzare. It is. It works.
        return next()
        # Literally no idea why this works.
        # sqlite3.InterfaceError: Error binding parameter 0 - probably
        # unsupported type.
        # This might be a bug in peewee.
    sel.set_select()
    print("Selected {}".format(sel))


@aliases("ls")
@wrap_errors([TMCError])
@needs_a_course
def listall():
    exercises = Course.get_selected().exercises
    print("ID{0}│ {1} │ {2} │ {3} │ {4}".format(
        (len(str(exercises[0].tid)) - 1) * " ",
        "S", "D", "C", "Name"
    ))
    for exercise in exercises:
        # ToDo: use a pager
        print("{0} │ {1} │ {2} │ {3} │ {4}".format(exercise.tid,
                                                   bts(exercise.is_selected),
                                                   btc(exercise.is_downloaded),
                                                   btc(exercise.is_completed),
                                                   exercise.name))


def bts(val):
    return "●" if val else " "


def btc(val):
    return "\033[32m✔\033[0m" if val else "\033[31m✘\033[0m"


@needs_a_course
@arg('command', help='The command')
@wrap_errors([TMCError])
def run(command):
    """
    Spawns a process with `command path-of-exercise`
    """
    exercise = Exercise.get_selected()
    Popen(['nohup', command, exercise.path()], stdout=DEVNULL, stderr=DEVNULL)


@aliases("init")
@aliases("conf")
def configure():
    if Config.has():
        sure = input("Override old configuration [y/N]: ")
        if sure.upper() != "Y":
            return
    db.reset()
    server = input("Server url [https://tmc.mooc.fi/mooc/]: ")
    if len(server) == 0:
        server = "https://tmc.mooc.fi/mooc/"
    while(True):
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        # wow, such security
        token = base64.b64encode(bytes("{0}:{1}".format(username, password),
                                       'utf-8')).decode("utf-8")
        try:
            api.configure(server, token)
        except Exception as e:  # ToDo: Better exception
            raise e
            if prompt_yn("Retry authentication", True):
                continue
            exit()
        break
    update(course=True)
    select("course")


@needs_a_course
def selpath():
    sel = Course.get_selected()
    defpath = os.path.join(os.path.expanduser("~"),
                           "tmc",
                           sel.name)
    path = input("File download path [{0}]: ".format(defpath))
    if len(path) == 0:
        path = defpath
    sel.path = path
    sel.save()
    dl = input("Download exercises [Y/n]: ")
    if dl.upper() == "Y" or len(dl) == 0:
        download("all")
    else:
        print("You can download the exercises with `tmc download all`")


def version():
    print("tmc.py version {0}".format(tmc.VERSION))
    print("Copyright 2014 Juhani Imberg")


def main():
    parser = argh.ArghParser()
    parser.add_commands([select, update, download, test, submit, next, resetdb,
                         configure, version, listall, run])
    parser.dispatch()


if __name__ == "__main__":
    main()
