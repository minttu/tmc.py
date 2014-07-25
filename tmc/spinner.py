import functools
import time
import threading
import sys


class Spinner(threading.Thread):

    """
    A spinny spinner.
    """

    def __init__(self, msg=""):
        threading.Thread.__init__(self)
        self.chars = ['\\', '|', '/', '-']
        self.template = "({0}) Please wait."
        self.msg = msg
        self.index = 0
        self.spinning = True

    def run(self):
        while self.spinning:
            if self.index != 0:
                sys.stdout.write("\b" * (len(self.template) - 2))
            sys.stdout.write(self.template.format(self.chars[self.index % 4]))
            sys.stdout.flush()
            self.index += 1
            time.sleep(0.05)

    def stopspin(self):
        self.spinning = False
        sys.stdout.write("\b" * (len(self.template) - 2)
                         + self.msg + " " * (len(self.template) - 2) + "\n")
        sys.stdout.flush()
        self.index = 0


def SpinnerDecorator(msg=""):
    def Decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            spin = Spinner(msg)
            spin.start()
            a = func(*args, **kwargs)
            spin.stopspin()
            spin.join()
            return a

        return wrapper

    return Decorator
