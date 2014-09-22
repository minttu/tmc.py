import sys

from tmc.config import Config
conf = Config()

from tmc.unicode_characters import UnicodePrint
sys.stdout = UnicodePrint(conf.use_unicode_characters)

from tmc.api import API
api = API()
