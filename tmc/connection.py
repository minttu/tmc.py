# -*- coding: utf-8 -*-

# tmccli / connection.py
# ======================
# 
# Handles connections to the TMC server and checking for errors.
# 
# Copyright © 2014 Juhani Imberg
# Released under the MIT License, see LICENSE for details

import requests
import os
import sys
from vlog import VLog as v
import zipfile
from course import Course
from exercise import Exercise
import shutil
import time
from config import Config
import subprocess
import glob
import xml.etree.ElementTree as ET
from StringIO import StringIO

class Connection:
    spinner = ['\\', '|', '/', '-']
    def __init__(self, conf):
        self.conf = conf
        self.server = conf.server
        self.auth = conf.auth
        self.force = False
        self.paste = False
        self.review = False
        self.update = False
        self.spinindex = 0

    def get_courses(self):
        r = requests.get("%scourses.json" % self.server,
            headers=self.auth,
            params={"api_version": 7})

        data = self.extract_json(r)

        courses = []
        for course in data["courses"]:
            courses.append(Course(int(course["id"]), course["name"]))
        return courses

    def get_course(self, course):
        if type(course) == int:
            id = course
        else:
            id = course.id
        r = requests.get("%scourses/%d.json" % (self.server, id),
            headers=self.auth,
            params={"api_version": 7})

        data = self.extract_json(r)
        
        newcourse = Course(int(data["course"]["id"]), data["course"]["name"])
        for i in data["course"]["exercises"]:
            tmp = Exercise(newcourse, int(i["id"]), i["name"])
            tmp.setDeadline(i["deadline_description"], i["deadline"])
            tmp.attempted = i["attempted"]
            tmp.completed = i["completed"]
            tmp.setDownloaded()
            newcourse.exercises.append(tmp)

        return newcourse

    def get_exercise(self, exercise):
        r = requests.get("%sexercises/%d.json" % (self.server, exercise),
            headers=self.auth,
            params={"api_version": 7})

        data = self.extract_json(r)

        if not "error" in data:
            course = Course(int(data["course_id"]), data["course_name"])
            exercise = Exercise(course, int(data["exercise_id"]), data["exercise_name"])
            exercise.setDownloaded()
            exercise.setDeadline(data["deadline"], data["deadline"])
            return exercise

        v.log(-1, "Could not find exercise %d" % exercise)
        return None

    def download_exercises(self, exercises):
        exercise = exercises[0]
        try:
            os.mkdir(exercise.course.name)
        except OSError:
            pass

        with open(os.path.join(exercise.course.name, ".tmc_course_id"), "w") as fp:
            fp.write(str(exercise.course.id))
            fp.close()

        for i in exercises:
            self.download_exercise(i)

    def download_exercise(self, exercise):
        dirname = os.path.join(exercise.course.name,
            exercise.name_week,
            exercise.name_name)

        tmpfile = StringIO()

        if os.path.isdir(dirname) and self.force == False and self.update == False:
            v.log(0, "Skipping \"%s\" since already extracted." % dirname)
            with open(os.path.join(dirname, ".tmc_exercise_id"), "w") as fp:
                fp.write(str(exercise.id))
                fp.close()
            with open(os.path.join(dirname, ".tmc_course_id"), "w") as fp:
                fp.write(str(exercise.course.id))
                fp.close()
            return

        r = requests.get("%sexercises/%d.zip" % (self.server, exercise.id),
            stream=True,
            headers=self.auth,
            params={"api_version": 7})
        
        for block in r.iter_content(1024):
            if not block:
                break
            tmpfile.write(block)

        dirname = os.path.join(exercise.course.name,
            exercise.name_week,
            exercise.name_name)

        if self.update == True:
            v.log(0, "Extracting/Updating \"%s\"" % dirname)
            zipfp = zipfile.ZipFile(tmpfile)
            for i in zipfp.infolist():
                if "/src/" not in i.filename:
                    zipfp.extract(i, exercise.course.name)
        else:
            v.log(0, "Extracting \"%s\"" % dirname)
            zipfp = zipfile.ZipFile(tmpfile)
            zipfp.extractall(exercise.course.name)

        with open(os.path.join(dirname, ".tmc_exercise_id"), "w") as fp:
            fp.write(str(exercise.id))
            fp.close()
        with open(os.path.join(dirname, ".tmc_course_id"), "w") as fp:
            fp.write(str(exercise.course.id))
            fp.close()

    # feels bad to place this here...
    def test_exercise(self, exercise, callback):
        if exercise.downloaded == False:
            v.log(-1, """Can't test something you have not even downloaded. 
                You might be in a wrong directory.""")
            exit(-1)
        v.log(0, "Testing %s locally. This will take a while." % exercise.name)

        # ant

        s = subprocess.Popen(["ant", "test", "-S"], stdout=open(os.devnull, "wb"), stderr=open(os.devnull, "wb"), cwd=os.path.join(os.getcwd(), exercise.course.name, exercise.name_week, exercise.name_name))
        s.communicate()

        files = glob.glob("%s*.xml" % (os.path.join(exercise.course.name, exercise.name_week, exercise.name_name, "build", "test", "results") + os.sep))

        for filename in files:
            try:
                with open(filename, "r") as fp:
                    root = ET.fromstring(fp.read())
                    fp.close()
                    for testcase in root.findall("testcase"):
                        dataarr = []
                        for failure in testcase.findall("failure"):
                            data = {}
                            data["message"] = failure.get("message")
                            data["success"] = False
                            dataarr.append(data)
                        callback(dataarr)
            except IOError:
                pass

        if len(files) == 0:
            v.log(-1, "Something wen't wrong with testing!")
            exit(-1)

    def submit_exercise(self, exercise, callback):
        if exercise.downloaded == False:
            v.log(-1, """Can't submit something you have not even downloaded. 
                You might be in a wrong directory.""")
            exit(-1)
        v.log(0, "Submitting %s. This will take a while." % exercise.name)


        v.log(1, "Zipping up")
        tmpfile = StringIO()
        dirname = os.path.join(exercise.course.name, exercise.name_week, exercise.name_name, "src")
        zipfp = zipfile.ZipFile(tmpfile, "w")
        for root, dirs, files in os.walk(dirname):
            for file in files:
                zipfp.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(dirname, '..')), zipfile.ZIP_DEFLATED)
        zipfp.close()

        params = {}
        if self.review == True:
            params["request_review"] = 1
        if self.paste == True:
            params["paste"] = 0

        r = requests.post("%s/exercises/%d/submissions.json" % (
            self.server, exercise.id),
            headers = self.auth,
            data = {"api_version": 7, "commit": "Submit"},
            params = params,
            files = {"submission[file]": ('submission.zip', tmpfile.getvalue())})

        data = self.extract_json(r)

        if "submission_url" in data:
            v.log(1, "Successfully submitted %s.\nPlease wait." % exercise.name)
            v.log(1, "URL: %s" % data["submission_url"])
        else:
            v.log(-1, "Didn't get a submission url. That's bad.")
        
        while self.check_submission_url(data["submission_url"], callback) == "processing":
            time.sleep(1)

    def check_submission_url(self, submission_url, callback):
        r = requests.get(submission_url, headers=self.auth)
        data = self.extract_json(r)
        self.spin()

        if data["status"] != "processing":
            data["id"] = submission_url.split("submissions/")[1].split(".json")[0]
            Config.last_submission(int(data["id"]))
            self.stopspin()
            callback(data)
        return data["status"]

    def select_course(self):
        data = self.get_courses()
        char = sys.stdin.read(1)
        print 'You pressed %s' % char

    def spin(self):
        if self.spinindex != 0:
            sys.stdout.write("\b")
        sys.stdout.write(Connection.spinner[self.spinindex%4])
        sys.stdout.flush()
        self.spinindex += 1

    def stopspin(self):
        if self.spinindex != 0:
            sys.stdout.write("\b")
            sys.stdout.flush()
        self.spinindex = 0

    def extract_json(self, request):
        if request is None:
            return

        json = None
        try:
            json = request.json()
        except ValueError:
            self.stopspin()
            if "500" in request.text:
                v.log(-1, "Server encountered a internal error. (500)")
            else:
                v.log(-1, "Didn't get valid JSON. This is a server problem.")
            exit(-1)

        if "error" in json:
            self.stopspin()
            v.log(-1, json["error"])
            exit(-1)

        return json

    def check_error(self, data):
        if "error" in data:
            return True
        return False