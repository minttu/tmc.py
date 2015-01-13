import sys
import os

# begin by checking for curses
try:
    import curses
except ImportError:
    if os.name == "nt":
        print("You seem to be running Windows. Please install curses",
              "from http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses")
    else:
        print("You don't have curses installed, please install it with",
              "your package manager.")
    exit(-1)

from tmc.config import Config
conf = Config()

from tmc.unicode_characters import UnicodePrint
sys.stdout = UnicodePrint(conf.use_unicode_characters)

from tmc.api import API
api = API()
