from requests import request
from requests.exceptions import RequestException
from functools import partial

from tmc.errors import APIError
from tmc.models import Config

# from tmc.version import __version__


class API:

    """Handles communication with TMC server."""

    def __init__(self):
        self.server_url = ""
        self.auth_header = ""
        self.configured = False
        self.api_version = 7
        # uncomment client and client_version after tmc.mooc.fi/mooc upgrades
        """ self.params = {
            "api_version": self.api_version,
            "client": "tmc.py",
            "client_version": __version__
        }"""
        self.params = {
            "api_version": self.api_version
        }

        # Essentially the same as requests.get and post
        # but uses _do_request as a single point of entry to
        # requests library
        self.get = partial(self._do_request, "GET")
        self.post = partial(self._do_request, "POST")

    def configure(self, url=None, token=None, test=False):
        """
        Configure the api to use given url and token or to get them from the
        Config.
        """

        if url is None:
            url = Config.get_value("url")
        if token is None:
            token = Config.get_value("token")

        self.server_url = url
        self.auth_header = {"Authorization": "Basic {0}".format(token)}
        self.configured = True

        if test:
            self.test_connection()

        Config.set("url", url)
        Config.set("token", token)

    def test_connection(self):
        self.make_request("courses.json")

    def make_request(self, slug, timeout=10):
        resp = self.get(slug, timeout=timeout)
        return self._to_json(resp)

    def get_courses(self):
        return self.make_request("courses.json")["courses"]

    def get_exercises(self, course_id):
        resp = self.make_request("courses/{0}.json".format(course_id))
        return resp["course"]["exercises"]

    def get_exercise(self, exercise_id):
        return self.make_request("exercises/{0}.json".format(exercise_id))

    def get_zip_stream(self, exercise_id, tmpfile_handle):
        slug = "exercises/{0}.zip".format(exercise_id)
        resp = self.get(slug, stream=True)

        for block in resp.iter_content(1024):
            if not block:
                break
            tmpfile_handle.write(block)

        return resp

    def send_zip(self, exercise_id, file, params):
        """
        Send zipfile to TMC for given exercise
        """
        slug = "exercises/{0}/submissions.json".format(exercise_id)
        resp = self.post(
            slug,
            params=params,
            files={
                "submission[file]": ('submission.zip', file)
            },
            data={
                "commit": "Submit"
            }
        )
        return self._to_json(resp)

    def get_submission(self, submission_id):
        resp = self.make_request("submissions/{0}.json".format(submission_id))
        if resp["status"] == "processing":
            return None
        return resp

    def _do_request(self, method, slug, **kwargs):
        """
        Does HTTP request sending / response validation.
        Prevents RequestExceptions from propagating
        """
        # ensure we are configured
        if not self.configured:
            self.configure()

        url = "{0}{1}".format(self.server_url, slug)

        # 'defaults' are values associated with every request.
        # following will make values in kwargs override them.
        defaults = {"headers": self.auth_header, "params": self.params}
        for item in defaults.keys():
            # override default's value with kwargs's one if existing.
            kwargs[item] = dict(defaults[item], **(kwargs.get(item, {})))

        # request() can raise connectivity related exceptions.
        # raise_for_status raises an exception ONLY if the response
        # status_code is "not-OK" i.e 4XX, 5XX..
        #
        # All of these inherit from RequestException
        # which is "translated" into an APIError.
        try:
            resp = request(method, url, **kwargs)
            resp.raise_for_status()
        except RequestException as e:
            reason = "HTTP {0} request to {1} failed: {2}"
            raise APIError(reason.format(method, url, repr(e)))
        return resp

    def _to_json(self, resp):
        """
            Extract json from a response.
            Assumes response is valid otherwise.
            Internal use only.
        """
        try:
            json = resp.json()
        except ValueError as e:
            reason = "TMC Server did not send valid JSON: {0}"
            raise APIError(reason.format(repr(e)))

        if "error" in json:
            raise APIError("JSON error: {0}".format(json["error"]))
        return json
