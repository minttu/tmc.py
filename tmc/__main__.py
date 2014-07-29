#!/usr/bin/env python3

import argh
from argh.decorators import aliases, arg
import getpass
import base64
import os
from functools import wraps
from subprocess import Popen, DEVNULL
from tmc.errors import (TMCError, NoCourseSelected, NoExerciseSelected,
                        NoSuchCourse, NoSuchExercise, APIError)
from tmc.prompt import yn_prompt, custom_prompt
from tmc.spinner import SpinnerDecorator
from tmc import db, api, files, menu, VERSION
from tmc.models import Course, Exercise, Config

import peewee

def selected_course(func):
    @wraps(func)
    def inner(*args, **kwargs):
        course = Course.get_selected()
        return func(course, *args, **kwargs)
    return inner


def selected_exercise(func):
    @wraps(func)
    def inner(*args, **kwargs):
        exercise = Exercise.get_selected()
        return func(exercise, *args, **kwargs)
    return inner


@aliases("reset")
def resetdb():
    """
    Resets the local database.
    """
    print("This won't remove any of your files,",
          "but instead the local database that tracks your progress.")
    if yn_prompt("Reset database", False):
        db.reset()
        print("Database resetted. You will need to tmc configure again.")


@aliases("up")
@arg("-c", "--course", action="store_true", help="Update courses instead.")
def update(course=False):
    """
    Update the metadata of courses and or exercises from server.
    """
    if course:
        @SpinnerDecorator("Updated course metadata.",
                          waitmsg="Updating course metadata.")
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

        @SpinnerDecorator("Updated exercise metadata.",
                          waitmsg="Updating exercise metadata.")
        def update_exercise():
            for exercise in api.get_exercises(selected.tid):
                old = None
                try:
                    old = Exercise.get(Exercise.tid == exercise["id"])
                except Exercise.DoesNotExist:
                    old = None
                if old is not None:
                    old.name = exercise["name"]
                    old.course = selected.id
                    old.is_attempted = exercise["attempted"]
                    old.is_completed = exercise["completed"]
                    old.deadline = exercise.get("deadline")
                    old.is_downloaded = os.path.isdir(old.path())
                    old.save()
                else:
                    ex = Exercise.create(tid=exercise["id"],
                                         name=exercise["name"],
                                         course=selected.id,
                                         is_attempted=exercise["attempted"],
                                         is_completed=exercise["completed"],
                                         deadline=exercise.get("deadline"))
                    ex.is_downloaded = os.path.isdir(ex.path())
                    ex.save()
        update_exercise()


@aliases("dl")
@arg("-f", "--force", default=False, action="store_true",
     help="Should the download be forced.")
@arg("-u", "--upgrade", default=False, action="store_true",
     help="Should the Java target be upgraded from 1.6 to 1.7")
@selected_course
def download(course, what="remaining", force=False, upgrade=False):
    """
    Download the exercises from the server.
    """
    what = what.upper()

    def dl(id):
        files.download_file(id, force=force, update_java=upgrade)

    if what == "ALL":
        for exercise in list(course.exercises):
            dl(exercise.tid)
    elif what == "REMAINING":
        for exercise in list(course.exercises):
            if not exercise.is_completed:
                dl(exercise.tid)
    else:
        dl(int(what))


@aliases("te")
@selected_course
def test(course, what=None):
    """
    Run tests on the selected exercise.
    """
    if what is not None:
        if not files.test(int(what)):
            exit(-1)
    else:
        sel = Exercise.get_selected()
        if not sel:
            raise NoExerciseSelected()
        files.test(sel.tid)


@aliases("su")
@arg("-p", "--pastebin", default=False, action="store_true",
     help="Should the submission be sent to TMC pastebin.")
@arg("-r", "--review", default=False, action="store_true",
     help="Request a review for this submission.")
@selected_course
def submit(course, what=None, pastebin=False, review=False):
    """
    Submit the selected exercise to the server.
    """
    if what is not None:
        files.submit(int(what), pastebin=pastebin, request_review=review)
    else:
        sel = Exercise.get_selected()
        if not sel:
            raise NoExerciseSelected()
        files.submit(sel.tid, pastebin=pastebin, request_review=review)


@aliases("sel")
@arg("-c", "--course", action="store_true", help="Select a course instead.")
@arg("-i", "--id", help="Select this ID without invoking the curses UI.")
def select(course=False, id=None):
    """
    Select a course or an exercise.
    """
    if course:
        update(course=True)
        og = None
        try:
            og = Course.get_selected()
        except NoCourseSelected:
            pass
        start_index = 0
        if og is not None:
            start_index = og.tid
        ret = id
        if not ret:
            ret = menu.launch("Select a course",
                              Course.select().execute(),
                              start_index)
        if ret != -1:
            try:
                sel = Course.get(Course.tid == ret)
            except peewee.DoesNotExist:
                raise NoSuchCourse()
            sel.set_select()
            update()
            if sel.path == "":
                select_a_path()
            oldex = None
            try:
                oldex = Exercise.get_selected()
            except TMCError:
                pass
            if oldex:
                oldex.is_selected = False
                oldex.save()
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
        ret = id
        if not ret:
            ret = menu.launch("Select an exercise",
                              Exercise.select().where(
                                  Exercise.course == sel.id).execute(),
                              start_index)
        if ret != -1:
            try:
                sel = Exercise.get(Exercise.tid == ret)
            except peewee.DoesNotExist:
                raise NoSuchExercise()
            sel.set_select()
            sel.course.set_select()
            print("Selected {}".format(sel))


@aliases("skip")
@selected_course
def next(course):
    """
    Go to the next exercise.
    """
    sel = None
    try:
        sel = Exercise.get_selected()
    except NoExerciseSelected:
        pass
    try:
        if sel is None:
            sel = [i for i in course.exercises][0]
        else:
            try:
                sel = Exercise.get(Exercise.id == sel.id + 1)
            except peewee.DoesNotExist:
                print("There are no more exercises in this course.")
                exit(-1)
    except peewee.InterfaceError:
        # OK. This looks bizzare. It is. It works.
        return next()
        # Literally no idea why this works.
        # sqlite3.InterfaceError: Error binding parameter 0 - probably
        # unsupported type.
        # This might be a bug in peewee.
    sel.set_select()
    print("Selected {}".format(sel))


@aliases("ls")
@selected_course
def listall(course):
    """
    Lists all of the exercises in the current course.
    """
    exercises = course.exercises
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


@arg('command', help='The command')
@selected_exercise
def run(exercise, command):
    """
    Spawns a process with `command path-of-exercise`
    """
    Popen(['nohup', command, exercise.path()], stdout=DEVNULL, stderr=DEVNULL)


@aliases("init", "conf")
def configure():
    """
    Configure tmc.py to use your account.
    """
    if Config.has():
        sure = input("Override old configuration [y/N]: ")
        if sure.upper() != "Y":
            return
    db.reset()
    server = input("Server url [https://tmc.mooc.fi/mooc/]: ")
    if len(server) == 0:
        server = "https://tmc.mooc.fi/mooc/"
    while True:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        # wow, such security
        token = base64.b64encode(bytes("{0}:{1}".format(username, password),
                                       'utf-8')).decode("utf-8")
        try:
            api.configure(server, token)
        except APIError as e:
            print(e)
            if yn_prompt("Retry authentication"):
                continue
            exit()
        break
    select(course=True)


@selected_course
def select_a_path(course):
    defpath = os.path.join(os.path.expanduser("~"),
                           "tmc",
                           course.name)
    path = input("File download path [{0}]: ".format(defpath))
    if len(path) == 0:
        path = defpath
    course.path = path
    course.save()
    ret = custom_prompt("Download exercises R: Remaining A: All N: None",
                        ["r", "a", "n"],
                        "r")
    if ret == "a":
        download("all")
    elif ret == "r":
        download("remaining")
    else:
        print("You can download the exercises with `tmc download all`")


def version():
    """
    Prints the version and exits.
    """
    print("tmc.py version {0}".format(VERSION))
    print("Copyright 2014 Juhani Imberg")


def main():
    parser = argh.ArghParser()
    parser.add_commands([select, update, download, test, submit, next, resetdb,
                         configure, version, listall, run])
    try:
        parser.dispatch()
    except TMCError as e:
        print(e)
        exit(-1)


if __name__ == "__main__":
    main()
