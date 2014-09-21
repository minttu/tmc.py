import xml.etree.ElementTree as ET
from os import path

from tmc.exercise_tests.basetest import BaseTest, TestResult


class CheckTest(BaseTest):

    def __init__(self):
        super().__init__("Check")

    def applies_to(self, exercise):
        return path.isfile(path.join(exercise.path(), "Makefile"))

    def test(self, exercise):
        _, _, err = self.run(["make", "clean", "all", "run-test"], exercise)
        ret = []

        testpath = path.join(exercise.path(), "test", "tmc_test_results.xml")
        if not path.isfile(testpath):
            return TestResult(False, err)

        ns = "{http://check.sourceforge.net/ns}"
        root = ET.parse(testpath).getroot()
        for test in root.iter(ns + "test"):
            success = True
            name = test.find(ns + "description").text
            message = None
            if test.get("result") == "failure":
                success = False
                message = test.find(ns + "message").text
            ret.append(TestResult(success=success, name=name, message=message))

        return ret
