import xml.etree.ElementTree as ET
from glob import glob
from os import path

from tmc.exercise_tests.basetest import BaseTest, TestResult


class AntTest(BaseTest):

    def __init__(self):
        super().__init__("Ant")

    def applies_to(self, exercise):
        return path.isfile(path.join(exercise.path(), "build.xml"))

    def test(self, exercise):
        returncode, out, err = self.run(["ant", "clean", "test"], exercise)
        ret = TestResult(success=(returncode == 0))

        if returncode != 0:
            tests = glob(path.join(exercise.path(),
                                   "build",
                                   "test",
                                   "results",
                                   "*.xml"))
            # If we have some results the compile went well
            if len(tests) > 0:
                for test in tests:
                    root = ET.parse(test).getroot()
                    for testcase in root.findall("testcase"):
                        for failure in testcase.findall("failure"):
                            ret.error += failure.text + "\n"
            # Otherwise we had a compile error, so lets go through stdout
            else:
                for line in out.split("\n"):
                    if "[javac] " in line:
                        ret.error += line.split("[javac] ")[1] + "\n"
            # If there still is no error, let's just hope theres something in
            # stderr to tell (such as that javac not found)
            if len(ret.error) == 0:
                ret.error = err

        return ret
