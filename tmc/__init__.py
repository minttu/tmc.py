from tmc.version import __version__ as version

from tmc.models import DB
from tmc.api import API


db = DB()
api = API()

import tmc.files
