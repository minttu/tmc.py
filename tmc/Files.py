import tmc
import zipfile
import os
import sys
from io import BytesIO, StringIO
from glob import glob
import subprocess
import xml.etree.ElementTree as ET


class Files:

    def __init__(self):
        pass

    def download_file(self, id):
        exercise = tmc.db.get_exercise(id)
        course = tmc.db.get_course(exercise["course_id"])
        outpath = os.path.join(course["path"])
        print("{0}exercises/{1}.zip -> {2}".format(tmc.api.server_url, exercise["id"], outpath))
        @tmc.Spinner.SpinnerDecorator("Done!")
        def inner(id):
            req = tmc.api.get_zip_stream(id)
            tmpfile = BytesIO()
            for block in req.iter_content(1024):
                if not block:
                    break
                tmpfile.write(block)
            zipfp = zipfile.ZipFile(tmpfile)
            zipfp.extractall(outpath)
            tmc.db.set_downloaded(id)
        inner(id)

    def test_ant(self, path):
        retcode = -1
        stderr = StringIO()
        out = None
        try:
            ret = subprocess.Popen(["ant", "clean", "test"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path)
            out = ret.communicate()[0].decode('utf-8')
            retcode = ret.returncode
        except OSError as e:
            if e.errno is os.errno.ENOENT:
                raise Exception("You don't seem to have ant installed.")
        if retcode != 0:
            sys.stderr.write("\033[31m")
            tests = glob(os.path.join(path, "build", "test", "results", "*.xml"))
            if len(tests) > 0:
                for test in tests:
                    tree = ET.parse(test)
                    root = tree.getroot()
                    for testcase in root.findall("testcase"):
                        for failure in testcase.findall("failure"):
                            sys.stderr.write(failure.text)
            else:
                for line in out.split("\n"):
                    if "[javac] " in line:
                        sys.stderr.write(line.split("[javac] ")[1] + "\n")
            sys.stderr.write("\033[0m")
            return False
        return True

    def test(self, id):
        exercise = tmc.db.get_exercise(id)
        course = tmc.db.get_course(exercise["course_id"])
        outpath = os.path.join(course["path"], "/".join(exercise["name"].split("-")))
        print("testing {0}".format(outpath))
        if exercise["downloaded"] == 0 or not os.path.isdir(outpath):
            raise Exception("That exercise is not downloaded!")
        # testing for what type of project this is
        if os.path.isfile(os.path.join(outpath, "build.xml")):
            return self.test_ant(outpath)
