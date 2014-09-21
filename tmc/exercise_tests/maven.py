import xml.etree.ElementTree as ET
from glob import glob
from os import path

from tmc.exercise_tests.basetest import BaseTest, TestResult


class MavenTest(BaseTest):

    def __init__(self):
        super().__init__("Maven")

    def applies_to(self, exercise):
        return path.isfile(path.join(exercise.path(), "pom.xml"))

    def test(self, exercise):
        returncode, out, err = self.run(["mvn", "clean", "test"], exercise)
        ret = []

        if returncode != 0:
            tests = glob(path.join(exercise.path(), "target",
                                   "surefire-reports", "*.xml"))
            # If we have some results the compile went well
            if len(tests) > 0:
                for test in tests:
                    root = ET.parse(test).getroot()
                    for testcase in root.findall("testcase"):
                        success = True
                        name = testcase.get("name")
                        message = None
                        trace = None
                        time = testcase.get("time", 0)
                        # any child existing = failure
                        for child in testcase:
                            success = False
                            message = child.get("message")
                            trace = child.text
                        ret.append(TestResult(success=success, name=name,
                                              message=message, trace=trace,
                                              time=time))
            # Otherwise we had a compile error, so lets go through stdout
            else:
                msg = ""
                if "[ERROR]" in out:
                    for line in out.split("\n"):
                        if "[ERROR] " in line:
                            msg += line.split("[ERROR] ")[1] + "\n"
                else:
                    msg = out
                ret.append(TestResult(success=False, name="Compile error",
                                      message=msg))
            if len(ret) == 0:
                ret.append(TestResult(success=False, name="Unknown error",
                                      message=err))
        return ret
