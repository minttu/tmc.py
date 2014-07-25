import zipfile
import os
import sys
from io import BytesIO, StringIO
from glob import glob
import subprocess
import xml.etree.ElementTree as ET
import time

from tmc.errors import *
from tmc.spinner import SpinnerDecorator
from tmc.models import Course, Exercise


class Files:

    def __init__(self, api):
        self.api = api

    def download_file(self, id, force=False):
        exercise = Exercise.get(Exercise.tid == id)
        course = exercise.get_course()
        outpath = os.path.join(course.path)
        realoutpath = exercise.path()
        print("{0}exercises/{1}.zip -> {2}".format(self.api.server_url,
                                                   exercise.tid,
                                                   realoutpath))
        if not force and os.path.isdir(realoutpath):
            print("Already downloaded, skipping.")
            exercise.is_downloaded = True
            exercise.save()
            return

        @SpinnerDecorator("Done!")
        def inner(id):
            req = self.api.get_zip_stream(id)
            tmpfile = BytesIO()
            for block in req.iter_content(1024):
                if not block:
                    break
                tmpfile.write(block)
            zipfp = zipfile.ZipFile(tmpfile)
            zipfp.extractall(outpath)
            exercise.is_downloaded = True
            exercise.save()
        inner(id)

    def test_ant(self, path):
        retcode = -1
        stderr = StringIO()
        out = None
        try:
            ret = subprocess.Popen(["ant", "clean", "test"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=path)
            out = ret.communicate()[0].decode('utf-8')
            retcode = ret.returncode
        except OSError as e:
            if e.errno is os.errno.ENOENT:
                raise Exception("You don't seem to have ant installed.")
        if retcode != 0:
            sys.stderr.write("\033[31m")
            tests = glob(
                os.path.join(path, "build", "test", "results", "*.xml"))
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
        print("Looking good.")
        return True

    def test(self, id):
        exercise = Exercise.get(Exercise.tid == id)
        course = exercise.get_course()
        outpath = exercise.path()
        print("testing {0}".format(outpath))
        if not os.path.isdir(outpath):
            raise Exception("That exercise is not downloaded!")
        exercise.is_downloaded = True
        exercise.save()
        # testing for what type of project this is
        if os.path.isfile(os.path.join(outpath, "build.xml")):
            return self.test_ant(outpath)
        print("Unknown project type")

    def submit(self, id, request_review=False, pastebin=False):
        exercise = Exercise.get(Exercise.tid == id)
        course = exercise.get_course()
        outpath = exercise.path()
        print("{0} -> {1}exercises/{2}.json".format(outpath,
                                                    self.api.server_url, id))
        outpath = os.path.join(outpath, "src")
        if not os.path.isdir(outpath):
            raise Exception("That exercise is not downloaded!")
        exercise.is_downloaded = True
        exercise.save()

        params = {}
        if request_review:
            params["request_review"] = "wolololo"
        if pastebin:
            params["paste"] = "wolololo"

        @SpinnerDecorator("Sent.")
        def inner():
            tmpfile = BytesIO()
            zipfp = zipfile.ZipFile(tmpfile, "w")
            for root, dirs, files in os.walk(outpath):
                for file in files:
                    zipfp.write(os.path.join(root, file),
                                os.path.relpath(
                                    os.path.join(
                                        root, file), os.path.join(
                                            outpath, '..')),
                                zipfile.ZIP_DEFLATED)
            zipfp.close()
            try:
                data = self.api.send_zip(id, tmpfile.getvalue(), params)
            except Exception as e:
                return e
            if data:
                return data
        resp = inner()
        if type(resp) == Exception or type(resp) == APIError:
            sys.stderr.write("\033[31m{0}\033[0m\n".format(resp))
            exit(-1)
        if "submission_url" in resp:
            @SpinnerDecorator("Results:")
            def inner():
                while True:
                    try:
                        data = self.api.get_submission(
                            int(resp["submission_url"].split(".json")[0].split("submissions/")[1]))
                    except Exception as e:
                        return e
                    if data:
                        return data
                    time.sleep(1)
            data = inner()
            if type(data) == Exception:
                sys.stderr.write("\033[31m{0}\033[0m".format(data))
                exit(-1)
            if data["status"] == "fail":
                sys.stderr.write("\033[31m")
                for testcase in data["test_cases"]:
                    if not testcase["successful"]:
                        sys.stderr.write("{0}:\n  {1}\n".format(
                            testcase["name"], testcase["message"]))
                sys.stderr.write(
                    "\033[33mFor better details run `tmc test " + str(id) + "`\033[0m\n")
                exit(-1)
            elif data["status"] == "ok":
                print("\033[32mPoints [{0}]\033[0m".format(
                    ", ".join(data["points"])))
            if "paste_url" in data:
                print("Pastebin: " + data["paste_url"])
            if data.get("requests_review", False):
                if data.get("reviewed", False):
                    print("This submission has been reviewed")
                else:
                    print("Requested a review")
