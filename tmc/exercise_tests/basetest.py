import os
from subprocess import PIPE, Popen

from tmc import conf
from tmc.coloring import errormsg, successmsg
from tmc.errors import MissingProgram, NoSuitableTestFound, NotDownloaded
from tmc.ui.spinner import Spinner


class TestResult(object):
    """
    Holds a testing result.
    """
    name = ""
    message = ""
    success = False
    time = None
    trace = ""

    def __init__(self, name=None, message=None, success=True,
                 time=None, trace=None):
        if name is None:
            name = ""
        if message is None:
            message = ""
        if trace is None:
            trace = ""
        self.name = name
        self.message = message
        self.success = success
        self.time = time
        self.trace = trace

    def print(self):
        msg = self.name
        if conf.tests_show_time and self.time is not None:
            msg += " ({0}s)".format(self.time)
        if self.success and conf.tests_show_trace:
            msg += "\n"
        if not self.success:
            msg += ": " + self.message
            if conf.tests_show_trace and self.trace:
                msg += "\n" + self.trace
            elif conf.tests_show_partial_trace and self.trace:
                msg += "\n" + "\n".join(self.trace.split("\n")[:5])
        if self.success and conf.tests_show_successful:
            successmsg(msg)
        elif not self.success:
            errormsg(msg)


class BaseTest(object):

    def __init__(self, name):
        self.name = name

    def run(self, params, exercise):
        """
        Run a program with Popen and handle common errors
        :param params: Parameter list to Popen
        :param exercise:
        :return: returncode, stdout, stderr
        """
        out, err, code = "", "", -1

        @Spinner.decorate("Results:", waitmsg="Testing with " + self.name)
        def inner():
            ret = Popen(params, stdout=PIPE, stderr=PIPE, cwd=exercise.path())
            out, err = ret.communicate()
            return out.decode("utf-8"), err.decode("utf-8"), ret.returncode
        try:
            out, err, code = inner()
        except OSError as e:
            if e.errno in [os.errno.ENOENT, os.errno.EACCES]:
                raise MissingProgram(params[0])
            else:
                raise e
        return code, out, err

    def applies_to(self, exercise):
        """
        Does this test apply to the given exercise.
        :param exercise:
        :return: True if applies to given exercise else False
        """
        raise NotImplementedError()

    def test(self, exercise):
        """
        Execute a test against given exercise.
        :param exercise:
        :return: TestResult
        """
        raise NotImplementedError()


def run_test(exercise):
    if not os.path.isdir(exercise.path()):
        raise NotDownloaded()
    ret = None
    for cls in BaseTest.__subclasses__():
        cls = cls()
        if cls.applies_to(exercise):
            ret = cls.test(exercise)
            break
    if ret is None:
        raise NoSuitableTestFound()
    result = True
    for i in ret:
        if not i.success:
            result = False
        i.print()
    if result:
        successmsg("OK!")
        return None
    return result
