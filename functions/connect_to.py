import mysql.connector

import environment
from ohm_lib.config import config


def connectTo(instanceName):
    from functions.time_zone_db import OhmMySQLConverter

    connInfo = getConnection(instanceName)
    conn = mysql.connector.connect(host=connInfo['host'], user=connInfo['user'], passwd=connInfo['password'],
                                   db=connInfo['database'], port=connInfo['port'], converter_class=OhmMySQLConverter)
    return conn


def getConnection(db):
    dbkey = db + '-db'
    if not dbkey in config():
        raise DatabaseNotFoundError("Can't find database config for instance %s" % (db))
    return config()[dbkey]


class DatabaseNotFoundError(Exception):
    pass
