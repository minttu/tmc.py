# -*- coding: utf-8 -*-

# tmccli / course.py
# ==================
# 
# Handles a course.
# 
# Copyright 2014 Juhani Imberg

class Course:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.raw = None
        self.exercises = []