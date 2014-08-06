import requests

from tmc.errors import APIError
from tmc.models import Config


# from tmc.version import __version__


class API:

    """Handles communication with TMC server."""

    def __init__(self):
        self.server_url = ""
        self.auth_header = ""
        self.configured = False
        self.tried_configuration = False
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

    def db_configure(self):
        url = Config.get_value("url")
        token = Config.get_value("token")
        self.configure(url, token)

    def configure(self, url, token):
        self.server_url = url
        self.auth_header = {"Authorization": "Basic {0}".format(token)}
        self.configured = True
        self.tried_configuration = True

        Config.set("url", url)
        Config.set("token", token)

    def make_request(self, slug, timeout=10):
        if not self.tried_configuration:
            self.db_configure()
        if not self.configured:
            raise APIError("API needs to be configured before use!")
        req = requests.get("{0}{1}".format(self.server_url, slug),
                           headers=self.auth_header,
                           params=self.params,
                           timeout=timeout)
        if req is None:
            raise APIError("Request is none!")
        return self.get_json(req)

    def get_json(self, req):
        json = None
        try:
            json = req.json()
        except ValueError:
            if "500" in req.text:
                raise APIError("TMC Server encountered a internal error.")
            else:
                raise APIError("TMC Server did not send valid JSON.")
        if "error" in json:
            raise APIError(json["error"])
        return json

    def get_courses(self):
        return self.make_request("courses.json")["courses"]

    def get_exercises(self, id):
        resp = self.make_request("courses/{0}.json".format(id))
        return resp["course"]["exercises"]

    def get_exercise(self, id):
        return self.make_request("exercises/{0}.json".format(id))

    def get_zip_stream(self, exercise):
        if not self.tried_configuration:
            self.db_configure()
        if not self.configured:
            raise APIError("API needs to be configured before use!")
        return requests.get("{0}exercises/{1}.zip".format(self.server_url,
                                                          exercise.tid),
                            stream=True,
                            headers=self.auth_header,
                            params=self.params)

    def send_zip(self, exercise, file, params):
        if not self.tried_configuration:
            self.db_configure()
        if not self.configured:
            raise APIError("API needs to be configured before use!")
        return self.get_json(
            requests.post(
                "{0}exercises/{1}/submissions.json".format(
                    self.server_url, exercise.tid),
                headers=self.auth_header,
                data={"api_version": self.api_version, "commit": "Submit"},
                params=params,
                files={"submission[file]": ('submission.zip', file)}))

    def get_submission(self, id):
        req = self.make_request("submissions/{0}.json".format(id))
        if req["status"] == "processing":
            return None
        return req
