import os
import sys
from subprocess import PIPE, Popen

from tmc.errors import MissingProgram, NoSuitableTestFound, NotDownloaded
from tmc.ui.spinner import Spinner


class TestResult(object):

    def __init__(self, success=True, error=""):
        self.success = success
        self.error = error

    def format(self):
        if len(self.error) > 0:
            sys.stderr.write("\033[31m{}\033[0m".format(self.error))
        if not self.success:
            return False
        sys.stdout.write("\033[32mOK!\033[0m\n")


class BaseTest(object):

    def __init__(self):
        raise NotImplementedError()

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
    return ret.format()
