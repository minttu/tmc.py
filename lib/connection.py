# -*- coding: utf-8 -*-

# tmccli / connection.py
# ======================
# 
# Handles connections to the TMC server and checking for errors.
# 
# Copyright 2014 Juhani Imberg

import requests
import os
import sys
from vlog import VLog as v
import zipfile
from course import Course
from exercise import Exercise
import shutil

class Connection:
    def __init__(self, server, auth):
        self.server = server
        self.auth = auth
        self.force = False

    def get_courses(self):
        r = requests.get("%scourses.json" % self.server,
            auth=self.auth,
            params={"api_version": 7})

        if self.check_error(r.json()):
            return None
        #return r.json()["courses"]
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

    def download_exercises(self, exercises):
        for i in exercises:
            self.download_exercise(i)

    def download_exercise(self, exercise):
        try:
            os.mkdir("tmp")
        except OSError:
            pass
        try:
            os.mkdir(exercise.course.name)
        except OSError:
            pass

        filename = os.path.join("tmp", "%i.zip" % exercise.id)

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

        if os.path.isdir(dirname) and not self.force:
            v.log(0, "Skipping \"%s\" since already extracted." % dirname)
        else:
            v.log(0, "Extracting \"%s\"" % dirname)
            zipfp = zipfile.ZipFile(filename)
            zipfp.extractall(exercise.course.name)

        os.remove(filename)

    def check_error(self, data):
        if "error" in data:
            return True
        return False