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

    def save(self):
        v.log(0, "Saving configuration file \"%s\"" % self.filename)
        data = {"username": self.username,
                "password": self.password,
                "server": self.server}
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
        self.auth = (self.username, self.password)

    def create_new(self):
        v.log(0, "Creating new configuration.")
        self.server = raw_input("Server url [http://tmc.mooc.fi/mooc/]: ")
        if len(self.server) == 0:
            self.server = "http://tmc.mooc.fi/mooc/"
        self.username = raw_input("Username: ")
        self.password = getpass.getpass("Password: ")
        self.save()