# -*- coding: utf-8 -*-

# tmccli / vlog.py
# ================
# 
# Simple logging that in theory is able to respect verbosity level.
# 
# Copyright © 2014 Juhani Imberg
# Released under the MIT License, see LICENSE for details

import sys

class VLog:
    level = 0
    @staticmethod
    def log(lvl, message):
        if lvl is -1:
            sys.stderr.write("\033[31m"+message+"\033[0m\n")
        elif lvl <= VLog.level:
            sys.stdout.write(message+"\n")