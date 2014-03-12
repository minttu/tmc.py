#!/usr/bin/env python3

import tmc
import argh
from argh.decorators import aliases
import getpass
import base64
import os


def resetdb():
    tmc.db.reset()


@aliases("up")
@tmc.Spinner.SpinnerDecorator("Updated.")
def update(what):
    what = what.upper()
    if what == "COURSES" or what == "C":
        for course in tmc.api.get_courses():
            tmc.db.add_course(course)
    elif what == "EXERCISES" or what == "E":
        sel = tmc.db.selected_course()
        if sel == None:
            return
        for exercise in tmc.api.get_exercises(sel["id"]):
            tmc.db.add_exercise(exercise, sel)


@aliases("dl")
@tmc.Spinner.SpinnerDecorator()
def download(what):
    what = what.upper()
    if what == "ALL":
        # ToDo: do something
        pass


@aliases("sel")
def select(what):
    what = what.upper()
    if what == "COURSE":
        og = tmc.db.selected_course()
        start_index = 0
        if og != None:
            start_index = og["id"]
        ret = tmc.Menu.launch(
            "Select a course", tmc.db.get_courses(), start_index)
        if ret != -1:
            tmc.db.select_course(ret)
            return True
        else:
            print("You can select the course with `tmc select course`")
            return False
    elif what == "EXERCISE":
        og = tmc.db.selected_exercise()
        start_index = 0
        if og != None:
            start_index = og["id"]
        ret = tmc.Menu.launch(
            "Select a exercise", tmc.db.get_exercises(), start_index)
        if ret != -1:
            tmc.db.select_exercise(ret)
            return True


@aliases("ls")
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
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    # wow, such security
    token = base64.b64encode(
        bytes("{0}:{1}".format(username, password), 'utf-8')).decode("utf-8")
    tmc.api.configure(server, token)
    update("courses")
    if select("course"):
        update("exercises")
        defpath = os.path.join(
            os.path.expanduser("~"), "tmc", tmc.db.selected_course()["name"])
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
        [select, update, download, resetdb, configure, version, listall])
    parser.dispatch()

if __name__ == "__main__":
    main()
