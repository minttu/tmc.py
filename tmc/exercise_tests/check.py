import xml.etree.ElementTree as ET
from os import path

from tmc.exercise_tests.basetest import BaseTest, TestResult


class CheckTest(BaseTest):

    def __init__(self):
        self.name = "Check"

    def applies_to(self, exercise):
        return path.isfile(path.join(exercise.path(), "Makefile"))

    def test(self, exercise):
        returncode, out, err = self.run(["make", "clean", "all", "run-test"],
                                        exercise)
        ret = TestResult()

        testpath = path.join(exercise.path(), "test", "tmc_test_results.xml")
        if not path.isfile(testpath):
            return TestResult(False, err)

        ns = "{http://check.sourceforge.net/ns}"
        root = ET.parse(testpath).getroot()
        for test in root.iter(ns + "test"):
            if test.get("result") == "failure":
                ret.success = False
                ret.error += test.find(ns + "message").text + "\n"

        return ret
