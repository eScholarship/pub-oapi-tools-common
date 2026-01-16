"""
This program connects to the pub-oapi-tools RDS.
"""

import pymysql
from misc import log


def get_connection(creds, cursor_class="DictCursor", verbose=False):
    log("INFO", __name__,
        f"Connecting to pub-oapi-tools RDS, database: {creds['database']}")
    log("INFO", __name__,
        f"This module uses the package pymysql: https://pymysql.readthedocs.io/en/latest/")

    # We typically use DictCursor, but other classes are available.
    # See here for more info
    # https://pymysql.readthedocs.io/en/latest/modules/cursors.html#

    if cursor_class == "DictCursor":
        cursor_class = pymysql.cursors.DictCursor
    elif cursor_class == "Cursor":
        cursor_class = pymysql.cursors.Cursor
    elif cursor_class == "SSCursor":
        cursor_class = pymysql.cursors.SSCursor
    elif cursor_class == "SSDictCursor":
        cursor_class = pymysql.cursors.SSDictCursor

    return pymysql.connect(
        host=creds['server'],
        user=creds['user'],
        password=creds['password'],
        database=creds['database'],
        cursorclass=cursor_class)
