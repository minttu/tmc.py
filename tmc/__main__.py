#!/usr/bin/env python3

import base64
import getpass
import os
import sys
from functools import wraps
from subprocess import DEVNULL, Popen

import argh
import peewee
from argh.decorators import aliases, arg
from tmc import api
from tmc.version import __version__
from tmc.files import download_exercise, submit_exercise
from tmc.errors import (APIError, NoCourseSelected, NoExerciseSelected,
                        NoSuchCourse, NoSuchExercise, TMCError, TMCExit)
from tmc.models import Config, Course, Exercise, reset_db
from tmc.ui.menu import Menu
from tmc.ui.prompt import custom_prompt, yn_prompt
from tmc.ui.spinner import Spinner
from tmc.exercise_tests.basetest import run_test


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


def false_exit(func):
    @wraps(func)
    def inner(*args, **kwargs):
        ret = func(*args, **kwargs)
        if ret == False:
            if "TMC_TESTING" in os.environ:
                raise TMCExit()
            else:
                sys.exit(-1)
        return ret
    return inner


@aliases("init", "conf")
@arg("-s", "--server", help="Server address to be used.")
@arg("-u", "--username", help="Username to be used.")
@arg("-p", "--password", help="Password to be used.")
@arg("-i", "--id", help="Course ID to be used.")
def configure(server=None, username=None, password=None, id=None):
    """
    Configure tmc.py to use your account.
    """
    if not server and not username and not password and not id:
        if Config.has():
            sure = input("Override old configuration [y/N]: ")
            if sure.upper() != "Y":
                return
    reset_db()
    if not server:
        server = input("Server url [https://tmc.mooc.fi/mooc/]: ")
        if len(server) == 0:
            server = "https://tmc.mooc.fi/mooc/"
    while True:
        if not username:
            username = input("Username: ")
        if not password:
            password = getpass.getpass("Password: ")
        # wow, such security
        token = base64.b64encode(bytes("{0}:{1}".format(username, password),
                                       'utf-8')).decode("utf-8")

        api.configure(server, token)
        try:
            api.make_request("courses.json")
        except APIError as e:
            print(e)
            if yn_prompt("Retry authentication"):
                continue
            exit()
        break
    if id:
        select(course=True, id=id, auto=True)
    else:
        select(course=True)


@aliases("cur")
@selected_exercise
def current(exercise):
    listall(single=exercise)


@aliases("dl")
@arg("-i", "--id", help="Download this ID.")
@arg("-a", "--all", default=False, action="store_true",
     help="Download all exercises.")
@arg("-f", "--force", default=False, action="store_true",
     help="Should the download be forced.")
@arg("-u", "--upgrade", default=False, action="store_true",
     help="Should the Java target be upgraded from 1.6 to 1.7")
@selected_course
def download(course, id=None, all=False, force=False, upgrade=False):
    """
    Download the exercises from the server.
    """

    def dl(id):
        download_exercise(Exercise.get(Exercise.tid == id),
                          force=force,
                          update_java=upgrade)

    if all:
        for exercise in list(course.exercises):
            dl(exercise.tid)
    elif id is not None:
        dl(int(id))
    else:
        for exercise in list(course.exercises):
            if not exercise.is_completed:
                dl(exercise.tid)
            else:
                exercise.update_downloaded()


@aliases("skip")
@selected_course
@false_exit
def next(course, num=1):
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
            for i in course.exercises:
                sel = i
                break
        else:
            try:
                sel = Exercise.get(Exercise.id == sel.id + num)
            except peewee.DoesNotExist:
                print("There are no more exercises in this course.")
                return False
    except peewee.InterfaceError:
        # OK. This looks bizzare. It is. It works.
        return next()
        # Literally no idea why this works.
        # sqlite3.InterfaceError: Error binding parameter 0 - probably
        # unsupported type.
        # This might be a bug in peewee.
    sel.set_select()
    listall(single=sel)
    # print("Selected {}".format(sel))


@aliases("prev")
def previous():
    next(num=-1)


@aliases("reset")
def resetdb():
    """
    Resets the local database.
    """
    print("This won't remove any of your files,",
          "but instead the local database that tracks your progress.")
    if yn_prompt("Reset database", False):
        reset_db()
        print("Database resetted. You will need to tmc configure again.")


@arg('command', help='The command')
@selected_exercise
def run(exercise, command):
    """
    Spawns a process with `command path-of-exercise`
    """
    Popen(['nohup', command, exercise.path()], stdout=DEVNULL, stderr=DEVNULL)


@aliases("sel")
@arg("-c", "--course", action="store_true", help="Select a course instead.")
@arg("-i", "--id", help="Select this ID without invoking the curses UI.")
def select(course=False, id=None, auto=False):
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
            ret = Menu.launch("Select a course",
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
                select_a_path(auto=auto)
            # Unselect the previously selected exercise
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
            ret = Menu.launch("Select an exercise",
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


@aliases("su")
@arg("-i", "--id", help="Submit this ID.")
@arg("-p", "--pastebin", default=False, action="store_true",
     help="Should the submission be sent to TMC pastebin.")
@arg("-r", "--review", default=False, action="store_true",
     help="Request a review for this submission.")
@selected_course
@false_exit
def submit(course, id=None, pastebin=False, review=False):
    """
    Submit the selected exercise to the server.
    """
    if id is not None:
        return submit_exercise(Exercise.byid(id),
                               pastebin=pastebin,
                               request_review=review)
    else:
        sel = Exercise.get_selected()
        if not sel:
            raise NoExerciseSelected()
        return submit_exercise(sel, pastebin=pastebin, request_review=review)


@aliases("te")
@arg("-i", "--id", help="Test this ID.")
@selected_course
@false_exit
def test(course, id=None):
    """
    Run tests on the selected exercise.
    """
    if id is not None:
        return run_test(Exercise.byid(id))
    else:
        sel = Exercise.get_selected()
        if not sel:
            raise NoExerciseSelected()
        return run_test(sel)


@aliases("ls")
@selected_course
def listall(course, single=None):
    """
    Lists all of the exercises in the current course.
    """

    def bs(val):
        return "●" if val else " "

    def bc(val):
        return "\033[32m✔\033[0m" if val else "\033[31m✘\033[0m"

    def format(exercise):
        return "{0} │ {1} │ {2} │ {3} │ {4}".format(exercise.tid,
                                                    bs(exercise.is_selected),
                                                    bc(exercise.is_downloaded),
                                                    bc(exercise.is_completed),
                                                    exercise.menuname())

    print("ID{0}│ {1} │ {2} │ {3} │ {4}".format(
        (len(str(course.exercises[0].tid)) - 1) * " ",
        "S", "D", "C", "Name"
    ))
    if single:
        print(format(single))
        return
    for exercise in course.exercises:
        # ToDo: use a pager
        print(format(exercise))


@aliases("up")
@arg("-c", "--course", action="store_true", help="Update courses instead.")
def update(course=False):
    """
    Update the metadata of courses and or exercises from server.
    """
    if course:
        @Spinner.decorate("Updated course metadata.",
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

        @Spinner.decorate("Updated exercise metadata.",
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


@selected_course
def select_a_path(course, auto=False):
    defpath = os.path.join(os.path.expanduser("~"),
                           "tmc",
                           course.name)
    if auto:
        path = defpath
    else:
        path = input("File download path [{0}]: ".format(defpath))
    if len(path) == 0:
        path = defpath
    course.path = path
    course.save()
    if auto:
        return
    ret = custom_prompt("Download exercises R: Remaining A: All N: None",
                        ["r", "a", "n"],
                        "r")
    if ret == "a":
        download(all=True)
    elif ret == "r":
        download()
    else:
        print("You can download the exercises with `tmc download --all`")


def version():
    """
    Prints the version and exits.
    """
    print("tmc.py version {0}".format(__version__))
    print("Copyright 2014 Juhani Imberg")


def main():
    parser = argh.ArghParser()
    parser.add_commands([select, update, download, test, submit, next, current,
                         previous, resetdb, configure, version, listall, run])
    try:
        parser.dispatch()
    except TMCError as e:
        print(e)
        exit(-1)


def run_command(argv):
    from io import StringIO
    if type(argv) == str:
        argv = [argv]
    parser = argh.ArghParser()
    parser.add_commands([select, update, download, test, submit, next, current,
                         previous, resetdb, configure, version, listall, run])
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    exception = None
    try:
        parser.dispatch(argv=argv)
    except Exception as e:
        exception = e
    return sys.stdout.getvalue(), sys.stderr.getvalue(), exception


if __name__ == "__main__":
    main()
