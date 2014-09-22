import xml.etree.ElementTree as ET
from glob import glob
from os import path

from tmc.exercise_tests.basetest import BaseTest, TestResult


class JavaTest(BaseTest):

    def __init__(self):
        super().__init__("Java")

    def applies_to(self, exercise):
        if path.isfile(path.join(exercise.path(), "pom.xml")):
            self.name = "Maven"
        elif path.isfile(path.join(exercise.path(), "build.xml")):
            self.name = "Ant"
        else:
            return False
        return True

    def test(self, exercise):
        prog = "ant" if self.name == "Ant" else "mvn"
        returncode, out, err = self.run([prog, "clean", "test"], exercise)
        ret = []

        if returncode != 0:
            if self.name == "Ant":
                tests = glob(path.join(exercise.path(), "build", "test",
                                       "results", "*.xml"))
            else:
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
                split = "[javac]" if self.name == "Ant" else "[ERROR]"
                msg = ""
                if split in out:
                    for line in out.split("\n"):
                        if split + " " in line:
                            msg += line.split(split + " ")[1] + "\n"
                else:
                    msg = out
                ret.append(TestResult(success=False, name="Compile error",
                                      message=msg))
            if len(ret) == 0:
                ret.append(TestResult(success=False, name="Unknown error",
                                      message=err))
        return ret
