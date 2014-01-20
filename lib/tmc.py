# -*- coding: utf-8 -*-

# tmccli / tmc.py
# ===============
# Copyright 2014 Juhani Imberg

import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import getpass
import argparse
import os
import time
import dateutil.parser
import datetime
import pytz
import shutil
import zipfile

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

'''
def vprint(level, message):
    if args is None:
        return
    if level is -1:
        sys.stderr.write(message+"\n")
    elif level <= args.verbose:
        sys.stdout.write(message+"\n")

def beautify(boolean):
    if boolean is True:
        return u"\033[32m✔\033[0m"
    else:
        return u"\033[31m✘\033[0m"

def handle_deadline(proper, message):
    if message is None:
        return "\033[32m                   Never!\033[0m"
    now = datetime.datetime.now(pytz.utc)
    then = dateutil.parser.parse(proper)
    if proper is None:
        return "\033[32m"+message+"\033[0m"
    if now < then:
        return "\033[32m"+message+"\033[0m"
    return "\033[31m"+message+"\033[0m"

def handle_status(status):
    if status == "ok":
        return "\033[32mOK!\033[0m"
    elif status == "error":
        return "\033[31mERROR\033[0m"
    return status

class Config:
    def __init__(self):
        self.data = {}
        self.data["username"] = ""
        self.data["password"] = ""
        self.data["server"] = ""
        self.data["courses"] = []
        self.can_authenticate = False
        self.filename = args.filename
        self.fresh = False
        self.course_fresh = False
        self.auth = None

    def save(self):
        vprint(1, "Saving configuration for later use. ("+self.filename+")")
        try:
            with open(self.filename, "w") as fp:
                json.dump(self.data, fp)
                fp.close()
        except IOError:
            vprint(-1, "Saving failed")

    def load(self):
        if self.fresh:
            return
        try:
            with open(self.filename, "r") as fp:
                vprint(1, "Earlier configuration found.")
                self.data = json.load(fp)
                fp.close()
                #self.test_auth()
                self.fresh = True
        except IOError:
            vprint(1, "No earlier cofiguration found.")
            self.create()
            self.test_auth()

    def create(self):
        vprint(0, "Creating new configuration.")
        self.data["server"] = raw_input("Server url [http://tmc.mooc.fi/mooc/]: ")
        if len(self.data["server"]) is 0:
            self.data["server"] = "http://tmc.mooc.fi/mooc/"
        self.data["username"] = raw_input("Username: ")
        self.data["password"] = getpass.getpass("Password: ")

    def get_auth(self):
        if self.auth is None:
            self.auth = HTTPBasicAuth(self.data["username"], self.data["password"])
        return self.auth

    def get_url(self, slug):
        return self.data["server"] + slug

    def test_auth(self):
        r = requests.get(self.get_url("courses.json"), params={"api_version": 7}, auth=self.get_auth())
        if "error" in r.json():
            vprint(-1, "Authentication failed!")
            exit()
        else:
            vprint(1, "Authentication was successfull!")
            self.can_authenticate = True
            self.save()

    def load_courses(self):
        if self.course_fresh:
            return
        self.load()
        r = requests.get(self.get_url("courses.json"), params={"api_version": 7}, auth=self.get_auth())
        self.data["courses"] = r.json()["courses"]
        self.save()
        self.course_fresh = True

    def get_course(self, id):
        self.load()
        self.load_courses()
        
        for i in self.data["courses"]:
            if i["id"] is id:
                return i
        return

    def list_courses(self):
        self.load()
        self.load_courses()

        print "id, name"
        for i in self.data["courses"]:
            print str(i["id"]) + ", " + i["name"]

    def init_course(self, course):
        self.load()
        if course is None:
            vprint(-1, "Couldn\'t find that course")
            return
        try:
            os.mkdir(course["name"])
            vprint(0, "Created new directory for course ("+course["name"]+")")
        except OSError:
            pass

    def save_course(self, data):
        try:
            os.mkdir(data["course"]["name"])
        except OSError:
            pass
        try:
            with open(os.path.join(data["course"]["name"], "data.json"), "w") as fp:
                json.dump(data, fp)
                fp.close()
        except IOError:
            vprint(-1, "Saving failed")

    def load_course(self, course):
        try:
            with open(os.path.join(course["name"], "data.json"), "r") as fp:
                vprint(1, "Loading course.")
                data = json.load(fp)
                fp.close()
                return data
        except IOError:
            vprint(1, "Failed loading course.")
            return self.download_course(course)

    def download_course(self, course):
        self.load()
        if course is None:
            vprint(-1, "Couldn\'t find that course")
            return

        vprint(0, "Downloading course metadata.")
        r = requests.get(self.get_url("courses/"+str(course['id'])+".json"), params={"api_version": 7}, auth=self.get_auth())
        self.save_course(r.json())
        return r.json()

    def list_exercises(self, course):
        self.load()
        if course is None:
            vprint(-1, "Couldn\'t find that course")
            return
        data = self.load_course(course)

        # ugh
        tmparr = [  ["d", "", ""],
                    ["o", "a", "c"],
                    ["w", "t", "o"],
                    ["n", "t", "m"],
                    ["l", "e", "p"],
                    ["o", "m", "l"],
                    ["a", "p", "e"],
                    ["d", "t", "t"],
                    ["e", "e", "e"]]
        for i in tmparr:
            print u"      │ %1s │ %1s │ %1s │" % (i[0], i[1], i[2])

        print u"%5s │ %1s │ %1s │ %1s │ %25s │ %s" % ("id", "d", "d", "d", "deadline", "name")
        print u"──────┼───┼───┼───┼───────────────────────────┼───────────────────"
        for i in data["course"]["exercises"]:
            print u"%5d │ %1s │ %1s │ %1s │ %25s │ %s" % (i["id"],
                                            beautify(self.is_downloaded(course, i)),
                                            beautify(i["attempted"]),
                                            beautify(i["completed"]),
                                            handle_deadline(i["deadline"], i["deadline_description"]),
                                            i["name"])

    def is_downloaded(self, course, exercise):
        if exercise is None:
            return False
        spl = exercise['name'].split("-")
        return os.path.isdir(os.path.join(course["name"], spl[0], spl[1]))

    def download_exercises(self, course):
        self.load()
        if course is None:
            vprint(-1, "Couldn\'t find that course")
            return
        self.download_course(course)
        data = self.load_course(course)

        vprint(0, "Downloading all exercises from "+course["name"])
        for i in data["course"]["exercises"]:
            filename = os.path.join(course["name"], str(i["id"])+".zip")
            dirname = course["name"]
            with open(filename, "wb") as fp:
                vprint(1, "Downloading "+filename)
                r = requests.get(i["zip_url"], auth=self.get_auth(), stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    fp.write(block)
            realdirname = os.path.join(dirname, i["name"].split("-")[0], i["name"].split("-")[1])
            if os.path.isdir(realdirname) and not args.force:
                vprint(0, "Skipping "+realdirname+" since already downloaded.")
            else:
                vprint(0, "Extracting "+realdirname)
                zipfp = zipfile.ZipFile(filename)
                zipfp.extractall(dirname)
            os.remove(filename)
        vprint(0, "Done!")

    def get_exercise(self, course, exercise_id):
        self.load()
        if course is None:
            vprint(-1, "Couldn\'t find that course")
            return
        data = self.load_course(course)
        for i in data["course"]["exercises"]:
            if i["id"] == exercise_id:
                return i

    def submit_exercise(self, course, exercise_id):
        exercise = self.get_exercise(course, exercise_id)
        if not self.is_downloaded(course, exercise):
            vprint(-1, "Can't submit something you have not even downloaded. You might be in a wrong directory.")
            exit(-1)
        vprint(0, "Submitting "+exercise["name"])
        vprint(1, "Zipping up")
        filename = os.path.join(course["name"], "submit_"+str(exercise["id"])+".zip")
        dirname = os.path.join(course["name"], exercise["name"].split("-")[0], exercise["name"].split("-")[1])
        zipfp = zipfile.ZipFile(filename, "w")
        for root, dirs, files in os.walk(dirname):
            for file in files:
                zipfp.write(os.path.join(root, file), os.path.join(exercise["name"].split("-")[0], os.path.relpath(os.path.join(root, file), os.path.join(dirname, '..'))), zipfile.ZIP_DEFLATED)
        zipfp.close()
        files = {"submission[file]": open(filename, "rb")}
        payload = {"api_version": 7, "commit": "Submit"}
        r = requests.post(exercise["return_url"], auth=self.get_auth(), data=payload, files=files)
        os.remove(filename)
        if 'submission_url' in r.json():
            vprint(0, "Successfully submitted %s. Submission URL: %s\nProcessing..." % (exercise["name"], r.json()["submission_url"]))
        while self.check_submission_url(r.json()["submission_url"]) == "processing":
            time.sleep(1)

    def check_submission_url(self, submission_url):
        r = requests.get(submission_url, auth=self.get_auth())
        data = r.json()
        if data["status"] != "processing":
            print u"Status: %s" % handle_status(data["status"])
            print u"Points: (%d/%d)" % (len(data["points"]), len(data["points"])+len(data["missing_review_points"]))
        return data["status"]

    def remove_everything(self):
        self.load()
        for i in self.data["courses"]:
            try:
                shutil.rmtree(i["name"])
            except OSError:
                pass

def main():

    parser = argparse.ArgumentParser(description="Python CLI for TestMyCode.", prog="tmc.py")
    parser.add_argument("--verbose", "-v", dest="verbose", action="count")
    parser.add_argument("--version", "-V", action="version", version="%(prog)s v1")
    parser.add_argument("--force", "-f", dest="force", action="store_true", default=False, help="force the operations")
    parser.add_argument("--config", "-C", dest="filename", action="store", default="tmc.json", help="alternative file to use for configuration")
    parser.add_argument("--auth", "-a", dest="command", action="store_const", const="auth", help="create authentication file")
    parser.add_argument("--list", "-l", dest="command", action="store_const", const="list", help="list all courses or exercises if --course is provided")
    parser.add_argument("--init", "-i", dest="command", action="store_const", const="init", help="initialize a folder for course id")
    parser.add_argument("--download", "-d", dest="command", action="store_const", const="download", help="downloads all exercises for course id")
    parser.add_argument("--submit", "-s", dest="command", action="store_const", const="submit", help="submit an exercise")
    parser.add_argument("--remove", dest="command", action="store_const", const="remove", help="removes everything")
    parser.add_argument("--course", "-c", dest="course_id", action="store", type=int, help="course id")
    parser.add_argument("--exercise", "-e", dest="exercise_id", action="store", type=int, help="exercise id")
    parser.add_argument("commands", metavar="COMMANDS", type=str, nargs="+", help="commands")
    global args
    args = parser.parse_args()
    if args.verbose is None:
        args.verbose = 0

    conf = Config()

    if args.command is None:
        args.command = "help"
    if args.force is None:
        args.force = False

    args.command = args.commands[0]

    if args.command == "auth":
        conf.load()
    elif args.command == "list":
        if args.course_id is None:
            conf.list_courses()
        else:
            conf.list_exercises(conf.get_course(args.course_id))
    elif args.command == "init":
        if args.course_id is None:
            vprint(-1, "You need to provide a course id (--course) for this command!")
            return
        conf.init_course(conf.get_course(args.course_id))
    elif args.command == "download":
        if args.course_id is None:
            vprint(-1, "You need to provide a course id (--course) for this command!")
            return
        conf.download_exercises(conf.get_course(args.course_id))
    elif args.command == "remove":
        if args.course_id is not None:
            pass
        elif args.exercise_id is not None:
            pass
        else:
            sure = raw_input("This will remove everything this script created. ARE YOU SURE?! [N/y] ")
            if sure.upper() == "Y":
                conf.remove_everything()
    elif args.command == "submit":
        if args.course_id is None:
            vprint(-1, "You need to provide a course id (--course) for this command!")
            return
        if args.exercise_id is None:
            vprint(-1, "You need to provide a exercise id (--exercise) for this command!")
            return
        conf.submit_exercise(conf.get_course(args.course_id), args.exercise_id)
    elif args.command == "help":
        parser.print_help()


if __name__ == "__main__":
    main()
'''