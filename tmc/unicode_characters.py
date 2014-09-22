import sys
import re


class UnicodePrint(object):
    """
    Very lazy class to replace stdout. It will strip a few unicode symbols and
    replace them with ASCII equivalents if the user has opted out of unicode
    stuff.
    """
    def __init__(self, unicode=True):
        self.use_unicode = unicode
        self.chars = {
            "✔": "Y",
            "✘": "N",
            "●": "X",
            "│": "|"
        }
        self.pattern = re.compile("|".join(self.chars.keys()))

    def write(self, text):
        if len(text) == 0:
            return
        if not self.use_unicode:
            text = self.pattern.sub(lambda x: self.chars[x.group()], text)
        sys.__stdout__.write(text)

    def __getattr__(self, attr):
        return getattr(sys.__stdout__, attr)
