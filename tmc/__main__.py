#!/usr/bin/env python3

import tmc
import argh
from argh.decorators import aliases
import getpass
import base64
import os
import sys
from functools import wraps

def needs_a_course(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if tmc.db.selected_course() is None:
            raise Exception("You need to select a course first!")
        return func(*args, **kwargs)
    return inner


def resetdb():
    tmc.db.reset()


@aliases("up")
@needs_a_course
def update():
    @tmc.Spinner.SpinnerDecorator()
    def update_exercise():
        sel = tmc.db.selected_course()
        for exercise in tmc.api.get_exercises(sel["id"]):
            tmc.db.add_exercise(exercise, sel)
    update_exercise()
    print("Done.")

@aliases("upc")
def updatecourses():
    @tmc.Spinner.SpinnerDecorator("Done.")
    def update_course():
        for course in tmc.api.get_courses():
            tmc.db.add_course(course)
    update_course()

@aliases("dl")
@needs_a_course
def download(what):
    what = what.upper()
    if what == "ALL":
        for exercise in tmc.db.get_exercises():
            tmc.files.download_file(exercise["id"])

@aliases("te")
@needs_a_course
def test(what=None):
    if what is not None:
        if not tmc.files.test(int(what)):
            exit(-1)

@aliases("su")
@needs_a_course
def submit(what=None):
    if what is not None:
        tmc.files.submit(int(what))

@aliases("sel")
def select(what):
    what = what.upper()
    if what == "COURSE":
        og = tmc.db.selected_course()
        start_index = 0
        if og is not None:
            start_index = og["id"]
        ret = tmc.Menu.launch(
            "Select a course", tmc.db.get_courses(), start_index)
        if ret != -1:
            tmc.db.select_course(ret)
            update()
            if tmc.db.selected_course()["path"] == "":
                selpath()
            return True
        else:
            print("You can select the course with `tmc select course`")
            return False
    elif what == "EXERCISE":
        og = tmc.db.selected_exercise()
        start_index = 0
        if og is not None:
            start_index = og["id"]
        ret = tmc.Menu.launch(
            "Select a exercise", tmc.db.get_exercises(), start_index)
        if ret != -1:
            tmc.db.select_exercise(ret)
            return True


@aliases("ls")
@needs_a_course
def listall():
    for exercise in tmc.db.get_exercises():
        # ToDo: use a pager
        print("{0} │ {1} │ {2} │ {3}".format(exercise["id"],
                                             unic(exercise["downloaded"]),
                                             unic(exercise["completed"]),
                                             exercise["name"]))


def unic(val):
    if val == 1:
        return "✔"
    else:
        return "✘"


@aliases("conf")
def configure():
    if tmc.db.hasconf():
        sure = input("Override old configuration [y/N]: ")
        if sure.upper() != "Y":
            return
    tmc.db.reset()
    server = input("Server url [http://tmc.mooc.fi/mooc/]: ")
    if len(server) == 0:
        server = "http://tmc.mooc.fi/mooc/"
    while(True):
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        # wow, such security
        token = base64.b64encode(bytes("{0}:{1}".format(username, password), 'utf-8')).decode("utf-8")
        try:
            tmc.api.configure(server, token)
        except Exception: # ToDo: Better exception
            if tmc.Prompt.prompt_yn("Retry authentication", True):
                continue
            exit()
        break
    updatecourses()
    select("course")

@needs_a_course
def selpath():
    defpath = os.path.join(os.path.expanduser("~"), "tmc", tmc.db.selected_course()["name"])
    path = input("File download path [{0}]: ".format(defpath))
    if len(path) == 0:
        path = defpath
    tmc.db.set_selected_path(path)
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
    parser.add_commands(
        [select, update, updatecourses, download, test, submit, resetdb, configure, version, listall])
    parser.dispatch()


if __name__ == "__main__":
    main()
