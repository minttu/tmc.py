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

        # Essentially the same as requests.get and post
        # but uses __do_request as a single point of entry to
        # requests library
        self.get = partial(self.__do_request, "GET")
        self.post = partial(self.__do_request, "POST")

    def __ensure_configured(f):
        ''' 
            Ensures that we are properly configured before making
            any requests to server

            API Internal use only.
        '''
        from functools import wraps
        @wraps(f)
        def wr(inst, *args, **kwargs):
            if not inst.tried_configuration:
                inst.db_configure()
            if not inst.configured:
                raise APIError("API needs to be configured before use!")
            return f(inst, *args, **kwargs)
        return wr

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

    @__ensure_configured
    def make_request(self, slug, timeout=10):
        url = "{0}{1}".format(self.server_url, slug)
        resp = self.get(url,
                   headers=self.auth_header,
                   params=self.params,
                   timeout=timeout)

        return self.__to_json(resp)

    def get_courses(self):
        return self.make_request("courses.json")["courses"]

    def get_exercises(self, id):
        resp = self.make_request("courses/{0}.json".format(id))
        return resp["course"]["exercises"]

    def get_exercise(self, id):
        return self.make_request("exercises/{0}.json".format(id))

    @__ensure_configured
    def get_zip_stream(self, exercise):
        tmpl = "{0}exercises/{1}.zip" 
        url = tmpl.format(self.server_url, exercise.tid)
        return self.get(url,
                   stream=True,
                   headers=self.auth_header,
                   params=self.params)

    @__ensure_configured
    def send_zip(self, exercise, file, params):
        tmpl = "{0}exercises/{1}/submissions.json"
        url = tmpl.format(self.server_url, exercise.tid)
        resp = self.post(
            url,
            headers=self.auth_header,
            params=params,
            files={
                "submission[file]": ('submission.zip', file)
            },
            data={
                "api_version": self.api_version, 
                "commit": "Submit"
            }
        )
        return self.__to_json(resp)

    def get_submission(self, id):
        req = self.make_request("submissions/{0}.json".format(id))
        if req["status"] == "processing":
            return None
        return req

    def __do_request(self, method, url, **kwargs):
        ''' 
            Does HTTP using Requests.
            Prevents RequestExceptions from propagating 
        '''
        #
        # request() can raise connectivity related exceptions.
        # raise_for_status raises an exception ONLY if the response 
        # status_code is "not-OK" i.e 4XX, 5XX..
        #
        # All of these inherit from RequestException
        #
        try:
            resp = request(method, url, **kwargs)
            resp.raise_for_status()
        except RequestException as e:
            reason = "HTTP {0} request to {1} failed: {2}"
            raise APIError(reason.format(method, url, repr(e)))

        return resp

    def __to_json(self, resp):
        '''
            Extract json from a response. 
            Assumes response is valid otherwise.
            Internal use only.
        '''
        try:
            json = resp.json()
        except ValueError as e:
            reason = "TMC Server did not send valid JSON: {0}"
            raise APIError(reason.format(repr(e)))

        if "error" in json:
            raise APIError("JSON error: {0}".format(json["error"]))
        return json

