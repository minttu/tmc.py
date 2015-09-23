import os
import time
import zipfile
from io import BytesIO

from tmc import api, conf
from tmc.errors import NotDownloaded, TMCError, WrongExerciseType
from tmc.ui.spinner import Spinner
from tmc.coloring import successmsg, warningmsg, errormsg, infomsg


def download_exercise(exercise, force=False, update_java=False, update=False):
    course = exercise.get_course()
    outpath = os.path.join(course.path)
    realoutpath = exercise.path()
    needs_update = update and exercise.is_downloaded
    print("{} -> {}".format(exercise.menuname(), realoutpath))
    if not force and os.path.isdir(realoutpath) and not update:
        print("Already downloaded, skipping.")
        exercise.is_downloaded = True
        exercise.save()
        if update_java:
            try:
                modify_java_target(exercise)
            except TMCError:
                pass
        return

    with Spinner.context(msg="Updated." if needs_update else "Downloaded.",
                         waitmsg="Downloading."):
        tmpfile = BytesIO()
        api.get_zip_stream(exercise, tmpfile)
        zipfp = zipfile.ZipFile(tmpfile)
        if needs_update:
            for i in zipfp.infolist():
                if "/src/" not in i.filename:
                    zipfp.extract(i, outpath)
        else:
            zipfp.extractall(outpath)
        exercise.is_downloaded = True
        exercise.save()

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
    infomsg("Submitting from:", outpath)
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

    resp = None

    with Spinner.context(msg="Submission has been sent.",
                         waitmsg="Sending submission."):
        tmpfile = BytesIO()
        with zipfile.ZipFile(tmpfile, "w") as zipfp:
            for root, _, files in os.walk(outpath):
                for file in files:
                    filename = os.path.join(root, file)
                    archname = os.path.relpath(os.path.join(root, file),
                                               os.path.join(outpath, '..'))
                    compress_type = zipfile.ZIP_DEFLATED
                    zipfp.write(filename, archname, compress_type)

        resp = api.send_zip(exercise, tmpfile.getvalue(), params)

    if "submission_url" not in resp:
        return

    url = resp["submission_url"]

    @Spinner.decorate(msg="Results:", waitmsg="Waiting for results.")
    def inner():
        while True:
            data = api.get_submission(url)
            if data:
                return data
            time.sleep(1)
    data = inner()

    success = True

    status = data["status"]

    if status == "fail":
        warningmsg("Some tests failed:")
        warningmsg("------------------")
        for test in data["test_cases"]:
            if test["successful"]:
                if conf.tests_show_successful:
                    successmsg("{name}: {message}".format(**test))
            else:
                errormsg("{name}:\n  {message}".format(**test))

        helper = "For better details run 'tmc test --id {0}'\n"
        warningmsg(helper.format(repr(exercise.tid)))
        success = False

    elif status == "ok":
        successmsg("All tests successful!")
        successmsg("---------------------")
        points = ", ".join(data["points"])
        successmsg("Points [{0}]".format(points))
        exercise.is_completed = exercise.is_attempted = True
        exercise.save()

    elif status == "error":
        warningmsg("Something went wrong :(")
        warningmsg("-----------------------")
        errormsg(data["error"])

    else:
        raise TMCError("Submission status unknown: {0}".format(status))

    if data.get("paste_url"):
        infomsg("Pastebin URL: " + data["paste_url"])

    if data.get("requests_review", False):
        if data.get("reviewed", False):
            infomsg("This submission has been reviewed")
        else:
            infomsg("Requested a review")

    infomsg("Submission URL: " + url.split(".json")[0])

    if not success:
        return False
