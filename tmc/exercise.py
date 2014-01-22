# -*- coding: utf-8 -*-

# tmccli / exercise.py
# ====================
# 
# Handles a exercise.
# 
# Copyright © 2014 Juhani Imberg
# Released under the MIT License, see LICENSE for details

import time
import dateutil.parser
import datetime
import pytz
import os

class Exercise:
    def __init__(self, course, id, name):
        self.id = id
        self.course = course
        self.name = name
        tmpname = name.split("-")
        if len(tmpname) > 1:
            self.name_week = name.split("-")[0]
            self.name_name = name.split("-")[1]
        else:
            self.name_week = ""
            self.name_name = name
        self.raw = None
        self.downloaded = False
        self.attempted = False
        self.completed = False
        self.deadline = "                    Never"
        self.has_time = True

    def setDeadline(self, description, isoformatted):
        if isoformatted is None:
            self.has_time = True
            return
        self.deadline = description
        now = datetime.datetime.now(pytz.utc)
        then = dateutil.parser.parse(isoformatted)
        self.has_time = now < then

    def setDownloaded(self):
        self.downloaded = os.path.isdir(os.path.join(self.course.name, self.name_week, self.name_name))