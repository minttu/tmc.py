# -*- coding: utf-8 -*-

# tmccli / pretty.py
# ==================
# 
# Pretty printing!
# 
# Copyright 2014 Juhani Imberg

class Pretty:
    @staticmethod
    def list_courses(courses):
        print u"%3s │ %s" % ("ID", "Name")
        print u"%s┼%s" % (u"─"*4, u"─"*26)
        for course in courses:
            print u"%3d │ %s" % (course.id, course.name)

    @staticmethod
    def list_exercises(exercises):

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

        print u"%5s │ %1s │ %1s │ %1s │ %25s │ %s" % (
            "id", "d", "d", "d", "deadline", "name")
        print u"%s┼───┼───┼───┼%s┼%s" % (u"─"*6, u"─"*27, u"─"*17)
        for exercise in exercises:
            print u"%5d │ %1s │ %1s │ %1s │ %25s │ %s" % (
                exercise.id,
                Pretty.boolean_to_pretty(exercise.downloaded),
                Pretty.boolean_to_pretty(exercise.attempted),
                Pretty.boolean_to_pretty(exercise.completed),
                Pretty.string_to_pretty(exercise.deadline, exercise.has_time),
                exercise.name)

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
