# Models are being split into multiple files. Some models have to be grouped together in one file
# otherwise they trigger a circular import. These are indicated in the files where "import *" is used.
from ._helpers import *

from .rel_user import RelUser
from .rel_user_multi import RelUserMulti
from .rel_user_text import RelUserText
from .user import User


from sqlalchemy import event
from sqlalchemy.pool import Pool

from functions.time_zone_db import OhmMySQLConverter


@event.listens_for(Pool, "checkout")
def check_connection(dbapi_con, con_record, con_proxy):
    if getattr(dbapi_con, 'ping', None):
        dbapi_con.ping(reconnect=True)
        dbapi_con.set_converter_class(OhmMySQLConverter)
