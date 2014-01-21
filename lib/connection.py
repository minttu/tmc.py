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

class Connection:
    spinner = ['\\', '|', '/', '-']
    def __init__(self, server, auth):
        self.server = server
        self.auth = auth
        self.force = False
        self.paste = False
        self.review = False
        self.spinindex = 0

    def get_courses(self):
        r = requests.get("%scourses.json" % self.server,
            auth=self.auth,
            params={"api_version": 7})

        if self.check_error(r.json()):
            return None
        courses = []
        for course in r.json()["courses"]:
            courses.append(Course(int(course["id"]), course["name"]))
        return courses

    def get_course(self, course):
        if type(course) == int:
            id = course
        else:
            id = course.id
        r = requests.get("%scourses/%d.json" % (self.server, id),
            auth=self.auth,
            params={"api_version": 7})

        if self.check_error(r.json()):
            return None
        
        newcourse = Course(int(r.json()["course"]["id"]), r.json()["course"]["name"])
        for i in r.json()["course"]["exercises"]:
            tmp = Exercise(newcourse, int(i["id"]), i["name"])
            tmp.setDeadline(i["deadline_description"], i["deadline"])
            tmp.attempted = i["attempted"]
            tmp.completed = i["completed"]
            tmp.setDownloaded()
            newcourse.exercises.append(tmp)

        return newcourse

    def get_exercise(self, course_id, exercise_id):
        course = self.get_course(course_id)
        for i in course.exercises:
            if i.id == exercise_id:
                return i
        v.log(-1, "Could not find exercise %d in course %d" % (exercise_id, course_id))
        return None

    def download_exercises(self, exercises):
        exercise = exercises[0]
        try:
            os.mkdir("tmp")
        except OSError:
            pass
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

        filename = os.path.join("tmp", "%i.zip" % exercise.id)

        if os.path.isdir(dirname) and self.force == False:
            v.log(0, "Skipping \"%s\" since already extracted." % dirname)
            with open(os.path.join(dirname, ".tmc_exercise_id"), "w") as fp:
                fp.write(str(exercise.id))
                fp.close()
            with open(os.path.join(dirname, ".tmc_course_id"), "w") as fp:
                fp.write(str(exercise.course.id))
                fp.close()
            return

        with open(filename, "wb") as fp:
            r = requests.get("%sexercises/%d.zip" % (self.server, exercise.id),
                stream=True,
                auth=self.auth,
                params={"api_version": 7})
            
            for block in r.iter_content(1024):
                if not block:
                    break
                fp.write(block)

        dirname = os.path.join(exercise.course.name,
            exercise.name_week,
            exercise.name_name)

        v.log(0, "Extracting \"%s\"" % dirname)
        zipfp = zipfile.ZipFile(filename)
        zipfp.extractall(exercise.course.name)

        with open(os.path.join(dirname, ".tmc_exercise_id"), "w") as fp:
            fp.write(str(exercise.id))
            fp.close()
        with open(os.path.join(dirname, ".tmc_course_id"), "w") as fp:
            fp.write(str(exercise.course.id))
            fp.close()

        os.remove(filename)

    def submit_exercise(self, exercise, callback):
        if exercise.downloaded == False:
            v.log(-1, """Can't submit something you have not even downloaded. 
                You might be in a wrong directory.""")
            exit(-1)
        v.log(0, "Submitting %s. This will take a while." % exercise.name)

        try:
            os.mkdir("tmp")
        except OSError:
            pass

        v.log(1, "Zipping up")
        filename = os.path.join("tmp", "submit_"+str(exercise.id)+".zip")
        dirname = os.path.join(exercise.course.name, exercise.name_week, exercise.name_name, "src")
        zipfp = zipfile.ZipFile(filename, "w")
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
            auth = self.auth,
            data = {"api_version": 7, "commit": "Submit"},
            params = params,
            files = {"submission[file]": open(filename, "rb")})

        os.remove(filename)

        if 'submission_url' in r.json():
            v.log(1, "Successfully submitted %s.\nPlease wait." % exercise.name)
            v.log(1, "URL: %s" % r.json()["submission_url"])
        
        while self.check_submission_url(r.json()["submission_url"], callback) == "processing":
            time.sleep(1)

    def check_submission_url(self, submission_url, callback):
        r = requests.get(submission_url, auth=self.auth)
        data = r.json()
        self.spin()
        if "error" in data:
            self.stopspin()
            v.log(-1, "Not authorized to view that submission or that submission doe\'s not exist!")
            exit(-1)
        if data["status"] != "processing":
            data["id"] = submission_url.split("submissions/")[1].split(".json")[0]
            Config.last_submission(int(data["id"]))
            self.stopspin()
            callback(data)
        return data["status"]

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

    def check_error(self, data):
        if "error" in data:
            return True
        return False