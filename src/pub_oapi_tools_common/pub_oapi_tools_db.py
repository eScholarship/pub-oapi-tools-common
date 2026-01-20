"""
Functions for working with the pub-oapi-tools DB
"""

import pymysql
from pub_oapi_tools_common.misc import log


def get_connection(creds=None, env=None, database=None, cursor_class="DictCursor", verbose=False):
    """
    Connects to the pub-oapi-tools RDS.

    Usage:
        get_connection(creds) -- see aws_lambda.py for expected dict input format
        or get_connection(env, database)

    Returns an open pymysql connection

    :param creds:
    :param env:
    :param database:
    :param cursor_class:
    :param verbose:
    :return:
    """

    log("INFO", __name__,
        (f"Connecting to pub-oapi-tools RDS."
         f"This module uses the package pymysql: https://pymysql.readthedocs.io/en/latest/"))

    if not (creds or (env and database)):
        log("ERROR", __name__,
            ("Must provide either 'creds', or 'env' and 'database'. "
             "Otherwise, we don't know what you want to connect to."))

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

    # User has supplied creds from parameter store
    if creds:
        return pymysql.connect(
            host=creds['server'],
            user=creds['user'],
            password=creds['password'],
            database=creds['database'],
            cursorclass=cursor_class)

    # Using the env and database name,
    else:
        from pub_oapi_tools_common.aws_lambda import get_parameters
        creds = {
            'tools-rds': {
                'folder': 'pub-oapi-tools/tools-rds',
                'env': env,
                'names': ['server', 'user', 'password']},
            'database': {
                'folder': 'pub-oapi-tools/tools-rds',
                'env': env,
                'names': [database]
            }}
        creds = get_parameters(creds)

        return pymysql.connect(
            host=creds['tools-rds']['server'],
            user=creds['tools-rds']['user'],
            password=creds['tools-rds']['password'],
            database=creds['database'][database],
            cursorclass=cursor_class)
