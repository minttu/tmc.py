from tmc.database import DB
from tmc.api import API
from tmc.files import Files

VERSION = version = "0.3.0"

db = DB()
api = API(version, db)
files = Files(db, api)
