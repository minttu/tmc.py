import re
import glob

import xml.etree.ElementTree as ET
from os import path, environ
import os
import stat

from tmc.exercise_tests.basetest import BaseTest, TestResult


class GTest(BaseTest):

    def __init__(self):
        super().__init__("GTest")

    def applies_to(self, exercise):
        return 0 < len(glob.glob(path.join(exercise.path(), "src", "*.cpp")))

    def find_test_executable(self, exercise):
        for file in glob.glob(path.join(exercise.path(), "test", "*")):
            if stat.S_IXUSR & os.stat(file)[stat.ST_MODE]:
                return file
        return None

    def test(self, exercise):
        _, _, err = self.run(["make", "clean", "all", "run-test"], exercise)
        ret = []

        testpath = path.join(exercise.path(), "test", "tmc_test_results.xml")
        if not path.isfile(testpath):
            return [TestResult(success=False, message=err)]

        if len(err) > 0:
            ret.append(TestResult(message=err, warning=True))

        xmlsrc = ""
        with open(testpath) as fp:
            xmlsrc = fp.read()

        xmlsrc = re.sub(r"&(\s)", r"&amp;\1", xmlsrc)

        root = ET.fromstring(xmlsrc)
        for test in root.iter("testcase"):
            name = test.get("name")
            if len(list(test)) > 0:
                result = list(test)[0]
                if result.tag == "failure":
                    success = False
                    message = result.get("message")
            else:
                success = True
                message = ""
            ret.append(TestResult(success=success, name=name, message=message))

        test_executable = self.find_test_executable(exercise)

        if test_executable:
            self.name = "Valgrind"  # TODO: This makes it say
                                    # "testing with valgrind", lets see if there
                                    # is a better way of doing that
            err, _, trace = self.run(["valgrind", "--leak-check=full",
                                      "--error-exitcode=1", test_executable],
                                     exercise, silent=True, env=dict(environ))
            success = err == 0
            ret.append(TestResult(success=success,
                                  name="valgrind",
                                  message=trace))

        return ret
