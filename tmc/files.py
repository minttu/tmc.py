import os
import sys
import time
import zipfile
from io import BytesIO

from tmc import api
from tmc.errors import APIError, NotDownloaded, TMCError, WrongExerciseType
from tmc.ui.spinner import Spinner


def download_exercise(exercise, force=False, update_java=False):
    course = exercise.get_course()
    outpath = os.path.join(course.path)
    realoutpath = exercise.path()
    print("{} -> {}".format(exercise.menuname(), realoutpath))
    if not force and os.path.isdir(realoutpath):
        print("Already downloaded, skipping.")
        exercise.is_downloaded = True
        exercise.save()
        if update_java:
            try:
                modify_java_target(exercise)
            except TMCError:
                pass
        return

    @Spinner.decorate("Downloaded.", waitmsg="Downloading.")
    def inner(exercise):
        req = api.get_zip_stream(exercise)
        tmpfile = BytesIO()
        for block in req.iter_content(1024):
            if not block:
                break
            tmpfile.write(block)
        zipfp = zipfile.ZipFile(tmpfile)
        zipfp.extractall(outpath)
        exercise.is_downloaded = True
        exercise.save()
    inner(exercise)

    if update_java:
        try:
            modify_java_target(exercise)
        except WrongExerciseType:
            pass


def modify_java_target(exercise, old="1.6", new="1.7"):
    path = os.path.join(exercise.path(), "nbproject", "project.properties")
    if not os.path.isfile(path):
        raise WrongExerciseType("java")
    lines = []
    with open(path) as fp:
        lines = fp.readlines()
    for ind, line in enumerate(lines):
        if line.startswith("javac") and line.endswith("=" + old + "\n"):
            lines[ind] = line.replace(old, new)
    with open(path, "w") as fp:
        fp.write("".join(lines))
    print("Changed Java target from {} to {}".format(old, new))


def submit_exercise(exercise, request_review=False, pastebin=False):
    outpath = exercise.path()
    print("{} -> {}".format(exercise.menuname(), "TMC Server"))
    outpath = os.path.join(outpath, "src")
    if not os.path.isdir(outpath):
        raise NotDownloaded()
    exercise.is_downloaded = True
    exercise.save()

    params = {}
    if request_review:
        params["request_review"] = "wolololo"
    if pastebin:
        params["paste"] = "wolololo"

    @Spinner.decorate("Submission has been sent.",
                      waitmsg="Sending submission.")
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
            data = api.send_zip(exercise, tmpfile.getvalue(), params)
        except Exception as e:
            return e
        if data:
            return data
    resp = inner()
    if type(resp) == Exception or type(resp) == APIError:
        sys.stderr.write("\033[31m{0}\033[0m\n".format(resp))
        return False
    if "submission_url" in resp:
        url = resp["submission_url"]
        submission_id = int(url.split(".json")[0].split("submissions/")[1])

        @Spinner.decorate("Results:", "Waiting for results.")
        def inner():
            while True:
                try:
                    data = api.get_submission(submission_id)
                except Exception as e:
                    return e
                if data:
                    return data
                time.sleep(1)
        data = inner()
        if type(data) == Exception:
            sys.stderr.write("\033[31m{0}\033[0m".format(data))
            return False
        success = True
        if data["status"] == "fail":
            sys.stderr.write("\033[31m")
            for testcase in data["test_cases"]:
                if not testcase["successful"]:
                    sys.stderr.write("{0}:\n  {1}\n".format(
                        testcase["name"], testcase["message"]))
            sys.stderr.write("".join(["\033[33mFor better details run `tmc"
                                      " test --id ", str(exercise.tid),
                                      "`\033[0m\n"]))
            success = False
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
        print("URL: " + url.split(".json")[0])
        if not success:
            return False
