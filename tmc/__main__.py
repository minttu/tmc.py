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


def needs_a_course(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if db.selected_course() is None:
            raise NoCourseSelected()
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
                db.add_course(course)
        update_course()
    else:
        if not db.selected_course():
            raise NoCourseSelected()

        @SpinnerDecorator()
        def update_exercise():
            sel = db.selected_course()
            for exercise in api.get_exercises(sel["id"]):
                db.add_exercise(exercise, sel)
        update_exercise()
        print("Done.")


@arg("-f", "--force", default=False,
     action="store_true", help="Should the download be forced.")
@aliases("dl")
@needs_a_course
@wrap_errors([TMCError])
def download(what="all", force=False):
    what = what.upper()
    if what == "ALL":
        for exercise in db.get_exercises():
            files.download_file(exercise["id"], force=force)
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
        sel = db.selected_exercise()
        if not sel:
            raise NoExerciseSelected()
        files.test(sel["id"])


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
        sel = db.selected_exercise()
        if not sel:
            raise NoExerciseSelected()
        files.submit(sel["id"], pastebin=pastebin, request_review=review)


@aliases("sel")
@wrap_errors([TMCError])
@arg("-c", "--course", action="store_true", help="Select a course instead.")
def select(course=False):
    if course:
        og = db.selected_course()
        start_index = 0
        if og is not None:
            start_index = og["id"]
        ret = menu.launch("Select a course", db.get_courses(), start_index)
        if ret != -1:
            db.select_course(ret)
            update()
            if db.selected_course()["path"] == "":
                selpath()
            next()
            return
        else:
            print("You can select the course with `tmc select --course`")
            return
    else:
        og = db.selected_exercise()
        start_index = 0
        if og is not None:
            start_index = og["id"]
        ret = menu.launch("Select a exercise", db.get_exercises(), start_index)
        if ret != -1:
            db.select_exercise(ret)
            print("Selected {}: {}".format(
                ret, db.selected_exercise()["name"]))


@needs_a_course
@wrap_errors([TMCError])
def next():
    sel = db.selected_exercise()
    exercises = db.get_exercises()
    next = 0
    if not sel:
        next = exercises[0]["id"]
    else:
        this = False
        for exercise in exercises:
            if sel["id"] == exercise["id"]:
                this = True
            elif this:
                next = exercise["id"]
                break
    db.select_exercise(next)
    print("Selected {}: {}".format(next, db.selected_exercise()["name"]))


@aliases("ls")
@wrap_errors([TMCError])
@needs_a_course
def listall():
    exercises = db.get_exercises()
    print("ID{0}│ {1} │ {2} │ {3} │ {4}".format(
        (len(str(exercises[0]["id"])) - 1) * " ",
        "S", "D", "C", "Name"
    ))
    for exercise in exercises:
        # ToDo: use a pager
        print("{0} │ {1} │ {2} │ {3} │ {4}".format(exercise["id"],
                                                   bts(exercise["selected"]),
                                                   btc(exercise["downloaded"]),
                                                   btc(exercise["completed"]),
                                                   exercise["name"]))


def bts(val):
    return "✔" if val == 1 else " "


def btc(val):
    return "\033[32m✔\033[0m" if val == 1 else "\033[31m✘\033[0m"


@needs_a_course
@arg('command', help='The command')
@wrap_errors([TMCError])
def run(command):
    """
    Spawns a process with `command path-of-exercise`
    """
    exercise = db.selected_exercise()
    if exercise:
        course = db.selected_course()
        p = os.path.join(course["path"], "/".join(exercise["name"].split("-")))
        Popen(['nohup', command, p], stdout=DEVNULL, stderr=DEVNULL)


@aliases("init")
@aliases("conf")
def configure():
    if db.hasconf():
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
            print(e)
            if prompt_yn("Retry authentication", True):
                continue
            exit()
        break
    update(course=True)
    select("course")


@needs_a_course
def selpath():
    defpath = os.path.join(
        os.path.expanduser("~"), "tmc", db.selected_course()["name"])
    path = input("File download path [{0}]: ".format(defpath))
    if len(path) == 0:
        path = defpath
    db.set_selected_path(path)
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
