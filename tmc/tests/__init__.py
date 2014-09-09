"""
Contains various test for nosetest.
"""

import os
import sys
from os import path

from tmc.__main__ import run_command
from tmc.errors import TMCExit
from tmc.version import __version__ as version


sys.path.append(os.getcwd())
from testsetup import (username, server_uri, course_id, exercise_id,
                       fail_file, fail_compile_file, success_file)


username = os.getenv("TMC_USERNAME", username)
password = os.getenv("TMC_PASSWORD", "")
server_uri = os.getenv("TMC_URI", server_uri)
course_id = os.getenv("TMC_CDI", course_id)
exercise_id = os.getenv("TMC_EID", exercise_id)


def test_version():
    """
    Prints the version correctly
    """
    stdout, _, _ = run_command("version")
    assert "tmc.py version {}".format(version) in stdout


def test_reset():
    """
    Database resetting works
    """
    import tmc.ui.prompt
    tmc.ui.prompt.input = lambda _: "y"
    stdout, _, _ = run_command("reset")
    assert "Database resetted." in stdout
    tmc.ui.prompt.input = lambda _: "n"
    stdout, _, _ = run_command("reset")
    assert "Database resetted." not in stdout


def test_configure():
    """
    Configuring works
    """
    _, _, ex = run_command(
        ["configure", "-u", username, "-p", password, "-s", server_uri,
         "-i", course_id, "--auto"]
    )
    assert ex is None


def test_next():
    """
    Next works
    """
    _, _, ex = run_command("next")
    assert ex is None


def test_previous():
    """
    Previous works
    """
    os.environ["TMC_TESTING"] = "1"

    _, _, ex = run_command("previous")
    assert ex is None

    _, _, ex = run_command("previous")
    assert ex is not None


def test_select():
    """
    Selecting works
    """
    _, _, ex = run_command(["select", "-i", exercise_id])
    assert ex is None


def test_download_single():
    """
    Downloading works
    """
    _, _, ex = run_command(["download", "-f", "-i", exercise_id])
    assert ex is None

    from tmc.models import Exercise

    assert Exercise.get_selected().is_downloaded == True


def test_test_fail():
    """
    Testing can fail
    """
    from tmc.models import Exercise

    fpath = path.join(Exercise.get_selected().path(), "src", "Nimi.java")
    with open(fpath, "w") as f:
        f.write(fail_file)

    os.environ["TMC_TESTING"] = "1"
    wasexit = False
    stdout, stderr, exception = run_command("test")
    if type(exception) == TMCExit:
        wasexit = True
    assert wasexit == True
    assert "Results:" in stdout
    assert "\033[31m" in stderr and "\033[0m" in stderr


def test_compile_fail():
    """
    Compile can fail
    """
    from tmc.models import Exercise

    fpath = path.join(Exercise.get_selected().path(), "src", "Nimi.java")
    with open(fpath, "w") as f:
        f.write(fail_compile_file)

    os.environ["TMC_TESTING"] = "1"
    wasexit = False
    stdout, stderr, exception = run_command("test")
    if type(exception) == TMCExit:
        wasexit = True
    assert wasexit == True
    assert "Results:" in stdout
    assert "\033[31m" in stderr and "\033[0m" in stderr


def test_test_success():
    """
    Testing can succeed
    """
    from tmc.models import Exercise

    fpath = path.join(Exercise.get_selected().path(), "src", "Nimi.java")
    with open(fpath, "w") as f:
        f.write(success_file)

    os.environ["TMC_TESTING"] = "1"
    wasexit = False
    stdout, stderr, exception = run_command("test")
    if type(exception) == TMCExit:
        wasexit = True
    assert wasexit == False
    assert "Results:" in stdout
    assert "\033[32m" in stdout and "\033[0m" in stdout
    assert len(stderr) == 0


def test_submit_fail():
    """
    Submitted exercise can fail
    """
    from tmc.models import Exercise

    fpath = path.join(Exercise.get_selected().path(), "src", "Nimi.java")
    with open(fpath, "w") as f:
        f.write(fail_file)

    os.environ["TMC_TESTING"] = "1"
    wasexit = False
    stdout, stderr, exception = run_command("submit")
    if type(exception) == TMCExit:
        wasexit = True
    assert wasexit == True
    assert "Results:" in stdout
    uri = os.getenv("TMC_URI", server_uri)
    assert "Submission URL: " + uri + "submissions/" in stdout
    assert "Pastebin: " + uri + "paste/" not in stdout
    assert "Requested a review" not in stdout
    assert "\033[31m" in stderr and "\033[0m" in stderr


def test_submit_success():
    """
    Submitted exercise can succeed
    """
    from tmc.models import Exercise

    fpath = path.join(Exercise.get_selected().path(), "src", "Nimi.java")
    with open(fpath, "w") as f:
        f.write(success_file)

    os.environ["TMC_TESTING"] = "1"
    wasexit = False
    stdout, stderr, exception = run_command(["submit", "-p", "-r"])
    if type(exception) == TMCExit:
        wasexit = True
    assert wasexit == False
    assert "Results:" in stdout
    assert "Points [1]" in stdout
    assert "Requested a review" in stdout
    uri = os.getenv("TMC_URI", server_uri)
    assert "Submission URL: " + uri + "submissions/" in stdout
    assert "Pastebin: " + uri + "paste/" in stdout

    assert len(stderr) == 0
