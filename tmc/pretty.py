# -*- coding: utf-8 -*-

# tmccli / pretty.py
# ==================
# 
# Pretty printing!
# 
# Copyright © 2014 Juhani Imberg
# Released under the MIT License, see LICENSE for details

import string

class Pretty:
    trace = False
    @staticmethod
    def list_courses(selected, courses):
        print u"%9s │ %2s │ %s" % ("selected", "ID", "Name")
        print u"%s┼%s┼%s" % (u"─"*10,u"─"*4, u"─"*26)
        for course in courses:
            print u"%s │ %2d │ %s" % (
                " "+string.center(Pretty.boolean_to_pretty(course.id == selected), 17),
                course.id,
                course.name)

    @staticmethod
    def list_exercises(selected, exercises):

        # ugh
        tmparr = [  ["", "d", "", ""],
                    ["", "o", "a", "c"],
                    ["s", "w", "t", "o"],
                    ["e", "n", "t", "m"],
                    ["l", "l", "e", "p"],
                    ["e", "o", "m", "l"],
                    ["c", "a", "p", "e"],
                    ["t", "d", "t", "t"],
                    ["e", "e", "e", "e"]]
        for i in tmparr:
            print u" %1s │      │ %1s │ %1s │ %1s │" % (i[0], i[1], i[2], i[3])

        print u" %1s │ %4s │ %1s │ %1s │ %1s │ %25s │ %s" % (
            "d", "id", "d", "d", "d", "deadline", "name")
        print u"───┼%s┼───┼───┼───┼%s┼%s" % (u"─"*6, u"─"*27, u"─"*17)
        for exercise in exercises:
            print u" %1s │ %4d │ %1s │ %1s │ %1s │ %25s │ %s" % (
                Pretty.boolean_to_pretty(exercise.id == selected),
                exercise.id,
                Pretty.boolean_to_pretty(exercise.downloaded),
                Pretty.boolean_to_pretty(exercise.attempted),
                Pretty.boolean_to_pretty(exercise.completed),
                Pretty.string_to_pretty(exercise.deadline, exercise.has_time),
                exercise.name)

    @staticmethod
    def print_submission(data):
        status = data["status"]
        if status == "ok":
            status = "\033[32mOK!\033[0m"
        elif status == "processing":
            status = "\033[33mprocessing\033[0m"
        elif status == "error":
            status = "\033[31mERROR!\033[0m"
        elif status == "fail":
            status = "\033[31mFAIL!\033[0m"
        id = int(data["id"])
        points = len(data["points"])
        maxpoints = points + len(data["missing_review_points"])

        if "processing_time" in data:
            processing_time = u" │ Processing time: %ss" % int(data["processing_time"])
        else:
            processing_time = ""

        if "paste_url" in data:
            paste = u" │ Paste: %s" % data["paste_url"]
        else:
            paste = ""

        if "requests_review" in data and "reviewed" in data:
            if data["requests_review"]:
                if data["reviewed"]:
                    review = u" │ Review: reviewed"
                else:
                    review = u" │ Review: requested"
            else:
                review = ""
        else:
            review = ""

        print u"ID: %d │ Status: %s │ Points: %d%s%s%s" % (id, status, points, processing_time, paste, review)
        if data["status"] == "fail":
            for i in data["test_cases"]:
                if not i["successful"]:
                    print " * \033[31m%s\033[0m" % i["message"]
                    if Pretty.trace:
                        for trace in i["exception"]["stackTrace"]:
                            print "%s:%d %s.%s" % (trace["fileName"], trace["lineNumber"], trace["declaringClass"], trace["methodName"])

            exit(-1)
        elif data["status"] == "error":
            print "\033[31m%s\033[0m" % data["error"]
            exit(-1)
        exit(0)

    @staticmethod
    def print_local_test(data):
        for i in data:
            print Pretty.string_to_pretty(i["message"], i["success"])
        if len(data) == 0:
            print Pretty.string_to_pretty("All good!", True)
            exit(0)
        else:
            exit(-1)
        

    @staticmethod
    def boolean_to_pretty(boolean):
        if boolean is True:
            return u"\033[32m✔\033[0m"
        else:
            return u"\033[31m✘\033[0m"

    @staticmethod
    def string_to_pretty(string, boolean):
        if boolean is True:
            return u"\033[32m%s\033[0m" % string
        else:
            return u"\033[31m%s\033[0m" % string