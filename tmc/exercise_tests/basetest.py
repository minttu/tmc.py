import os
from subprocess import PIPE, Popen

from tmc import conf
from tmc.coloring import errormsg, successmsg, warningmsg
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

    def __init__(self, name="", message="", success=True, warning=False,
                 time=None, trace=""):
        self.name = name
        self.message = message
        self.success = success
        self.warning = warning
        self.time = time
        self.trace = trace

    def print(self):
        msg = self.name
        if self.warning:
            return warningmsg(self.message)
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
            successmsg(msg, "OK!")
        elif not self.success:
            errormsg(msg)


class BaseTest(object):

    def __init__(self, name):
        self.name = name

    def run(self, params, exercise, silent=False, env=os.environ):
        """
        Run a program with Popen and handle common errors
        :param params: Parameter list to Popen
        :param exercise:
        :return: returncode, stdout, stderr
        """
        out, err, code = "", "", -1

        @Spinner.decorate("Results:" if not silent else "",
                          waitmsg="Testing with " + self.name)
        def inner():
            ret = Popen(params, stdout=PIPE, stderr=PIPE, cwd=exercise.path(),
                        env=env)
            out, err = ret.communicate()
            return (out.decode("utf-8", "backslashreplace"),
                    err.decode("utf-8", "backslashreplace"),
                    ret.returncode)
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


def select_test_class(exercise):
    classes = BaseTest.__subclasses__()
    class_instances = (c() for c in classes)

    # next returns the first element in sequence, or None
    pred = lambda c: c.applies_to(exercise)
    cls = next(filter(pred, class_instances), None)

    if cls is None:
        raise NoSuitableTestFound()
    return cls


def run_test(exercise):
    if not os.path.isdir(exercise.path()):
        raise NotDownloaded()

    test_class = select_test_class(exercise)
    results = test_class.test(exercise)
    all_ok = all(r.success for r in results)

    for r in results:
        r.print()

    if all_ok:
        successmsg("All OK!")
        return None
    return all_ok
