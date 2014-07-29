from tmc.version import __version__ as version

from tmc.models import DB
from tmc.api import API
from tmc.files import Files

db = DB()
api = API()
files = Files(api)
