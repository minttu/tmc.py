# -*- coding: utf-8 -*-

# tmccli / config.py
# ==================
# 
# Manages tmc_config.json for the required auth credentials.
# 
# Copyright 2014 Juhani Imberg

import json
import sys
import getpass
from vlog import VLog as v

class Config:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.server = ""
        self.auth = ()
        self.filename = "tmc_config.json"
        self.default_course = -1

    def save(self):
        v.log(0, "Saving configuration file \"%s\"" % self.filename)
        data = {"username": self.username,
                "password": self.password,
                "server": self.server,
                "default_course": self.default_course}
        try:
            with open(self.filename, "w") as fp:
                json.dump(data, fp)
                fp.close()
        except IOError:
            v.log(-1, "Could not save file \"%s\"" % self.filename)
            exit(-1)

    def load(self):
        v.log(1, "Loading configuration from \"%s\"" % self.filename)
        data = None
        try:
            with open(self.filename, "r") as fp:
                data = json.load(fp)
                fp.close()
        except IOError:
            v.log(-1, "Could not load configuration. Run \"tmc init\" first!")
            exit(-1)
        self.username = data["username"]
        self.password = data["password"]
        self.server = data["server"]
        if "default_course" in data:
            self.default_course = data["default_course"]
        self.auth = (self.username, self.password)

    def create_new(self):
        v.log(0, "Creating new configuration.")
        self.server = raw_input("Server url [http://tmc.mooc.fi/mooc/]: ")
        if len(self.server) == 0:
            self.server = "http://tmc.mooc.fi/mooc/"
        self.username = raw_input("Username: ")
        self.password = getpass.getpass("Password: ")
        self.save()

    def set_course(self, id):
        self.default_course = id
        v.log(0, "Setting default course ID to %i" % int(id))
        self.save()

    def unset_course(self):
        self.default_course = -1
        v.log(0, "Resetted default course ID")
        self.save()