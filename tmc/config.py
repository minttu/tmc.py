import os

from os import path, environ
from configparser import ConfigParser
from collections import OrderedDict


class Config(object):
    """
    This class will take care of ConfigParser and writing / reading the
    configuration.

    TODO: What to do when there are more variables to be configured? Should we
    overwrite the users config file with the updated variables if the file is
    lacking?
    """

    config = None
    filename = ""
    defaults = None

    def __init__(self):
        default_path = path.join(path.expanduser("~"), ".config", "tmc.ini")
        config_filepath = environ.get("TMC_CONFIGFILE", default_path)
        super().__setattr__('filename', config_filepath)
        super().__setattr__('config', ConfigParser())
        self._update_defaults()

        self.config["CONFIGURATION"] = {}

        for i in self.defaults:
            self.config["CONFIGURATION"][i] = str(self.defaults[i])
        if self._exists():
            self._load()

        self._write()

    def _update_defaults(self):
        defaults = OrderedDict()
        if os.name == "nt":
            defaults["use_unicode_characters"] = False
            defaults["use_ansi_colors"] = False
        else:
            defaults["use_unicode_characters"] = True
            defaults["use_ansi_colors"] = True
        defaults["tests_show_trace"] = False
        defaults["tests_show_partial_trace"] = False
        defaults["tests_show_time"] = True
        defaults["tests_show_successful"] = True
        super().__setattr__('defaults', defaults)

    def _exists(self):
        return path.isfile(self.filename)

    def _write(self):
        d = os.path.dirname(self.filename)
        if not os.path.exists(d):
            os.makedirs(d)
        with open(self.filename, "w") as fp:
            self.config.write(fp)

    def _load(self):
        with open(self.filename, "r") as fp:
            self.config.read_file(fp)
        for i in self.config["CONFIGURATION"]:
            if i not in self.defaults:
                print("Warning: unknown configuration option: " + i)

    def __getattr__(self, name):
        if isinstance(self.defaults.get(name), bool):
            return self.config["CONFIGURATION"].getboolean(name)
        return self.config["CONFIGURATION"].get(name)

    def __setattr__(self, name, value):
        self.config["CONFIGURATION"][name] = str(value)
