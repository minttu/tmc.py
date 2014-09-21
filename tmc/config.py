from os import path, environ
from configparser import ConfigParser


class Config(object):
    """
    This class will take care of ConfigParser and writing / reading the
    configuration.

    TODO: What to do when there are more variables to be configured? Should we
    overwrite the users config file with the updated variables if the file is
    lacking?
    """

    defaults = {"use_unicode_characters": True,
                "use_ansi_colors": True,
                "tests_show_trace": False,
                "tests_show_partial_trace": False,
                "tests_show_time": True,
                "tests_show_successful": True}
    config = None
    filename = ""

    def __init__(self):
        super().__setattr__('filename',
                            environ.get("TMC_CONFIGFILE",
                                        path.join(path.expanduser("~"),
                                                  ".config",
                                                  "tmc.ini")))
        super().__setattr__('config', ConfigParser())

        self.config["CONFIGURATION"] = {}
        for i in self.defaults:
            self.config["CONFIGURATION"][i] = str(self.defaults[i])

        if self._exists():
            self._load()
        else:
            self._create_with_defaults()

    def _exists(self):
        return path.isfile(self.filename)

    def _create_with_defaults(self):
        with open(self.filename, "w") as fp:
            print("Created configuration file to {}".format(self.filename))
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
