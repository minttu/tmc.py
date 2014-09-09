from os import path
from configparser import ConfigParser


class Config(object):
    """
    This class will take care of ConfigParser and writing / reading the
    configuration.

    TODO: What to do when there are more variables to be configured? Should we
    overwrite the users config file with the updated variables if the file is
    lacking?
    """

    def __init__(self):
        self.filename = path.join(path.expanduser("~"), ".config", "tmc.ini")
        self.config = ConfigParser()

        if self._exists():
            self._load()
        else:
            self._create_with_defaults()

    def _exists(self):
        return path.isfile(self.filename)

    def _create_with_defaults(self):
        self.config["CONFIGURATION"] = {
            "use_unicode_characters": "yes",
            "use_ansi_colors": "yes",
            "show_successful_tests": "yes"
        }
        with open(self.filename, "w") as fp:
            print("Created configuration file to {}".format(self.filename))
            self.config.write(fp)

    def _load(self):
        with open(self.filename, "r") as fp:
            self.config.read_file(fp)

    def get(self, name, default=None):
        # This is because getboolean handles yes and no by default. Oh and
        # bool('false') is true.
        if "use" in name or "show" in name:
            return self.config["CONFIGURATION"].getboolean(name, default)
        else:
            return self.config["CONFIGURATION"].get(name, default)

    def use_unicode_characters(self):
        return self.get("use_unicode_characters", True)

    def use_ansi_colors(self):
        return self.get("use_ansi_colors", False)

    def show_successful_tests(self):
        return self.get("show_successful_tests", False)
