import functools
import sys
import threading
import time


class Spinner(threading.Thread):

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

    def stop_spinning(self):
        self.spinning = False
        sys.stdout.write("\b" * (len(self.template) - 2)
                         + self.msg + " " * (len(self.template) - 2) + "\n")
        sys.stdout.flush()
        self.index = 0

    @staticmethod
    def decorate(msg="", waitmsg="Please wait"):
        """
        Decorated methods progress will be displayed to the user as a spinner.
        Mostly for slower functions that do some network IO.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                spin = Spinner(msg=msg, waitmsg=waitmsg)
                spin.start()
                a = None
                try:
                    a = func(*args, **kwargs)
                except Exception as e:
                    spin.msg = "Something went wrong: "
                    spin.stop_spinning()
                    spin.join()
                    raise e
                spin.stop_spinning()
                spin.join()
                return a

            return wrapper

        return decorator
