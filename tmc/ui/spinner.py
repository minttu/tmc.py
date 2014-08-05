import functools
import sys
import threading
import time


class Spinner(threading.Thread):

    """
    A spinny spinner.
    """

    def __init__(self, msg="", waitmsg="Please wait"):
        threading.Thread.__init__(self)
        self.chars = ['\\', '|', '/', '-']
        self.template = "({0}) " + waitmsg
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

    @staticmethod
    def decorate(msg="", waitmsg="Please wait"):
        def Decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                spin = Spinner(msg=msg, waitmsg=waitmsg)
                spin.start()
                a = None
                try:
                    a = func(*args, **kwargs)
                except Exception as e:
                    spin.msg = "Something went wrong: "
                    spin.stopspin()
                    spin.join()
                    raise e
                spin.stopspin()
                spin.join()
                return a

            return wrapper

        return Decorator
