"""
Functions for working with the eScholarship MySQL DB
"""

import pymysql
from pub_oapi_tools_common.misc import log


def get_connection(creds: dict = None,
                   env: str = None,
                   database: str = None,
                   cursor_class: str = "DictCursor"
                   ) -> pymysql.connections.Connection:
    """
    Connects to the eScholarship MySQL database.

    Usage:
        get_connection(creds) -- see aws_lambda.py for expected dict input format
        or get_connection(env, database)

    :param creds: A dict containing driver, server, database, user, and password key/values.
    :param env: Presently, "prod" is the only env here.
    :param database: Name of the DB to connect to.
    :param cursor_class: (String) name of a PyMySQL cursor class:
        Cursor, DictCursor (default), SSCursor, or SSDictCursor. See here
        https://pymysql.readthedocs.io/en/latest/modules/cursors.html#
    :return: An open PyMySQL connection.
    """

    log("INFO", __name__,
        (f"Connecting to eScholarship database. "
         f"This module uses the package pymysql: "
         f"https://pymysql.readthedocs.io/en/latest/"))

    if not (creds or (env and database)):
        log("ERROR", __name__,
            ("Must provide either 'creds', or 'env' and 'database'. "
             "Otherwise, we don't know what you want to connect to."))

    # We typically use DictCursor, but other classes are available.
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
            'eschol-db': {
                'folder': 'pub-oapi-tools/eschol-db',
                'env': env
            }
        }
        creds = get_parameters(creds)

        return pymysql.connect(
            host=creds['eschol-db']['server'],
            user=creds['eschol-db']['user'],
            password=creds['eschol-db']['password'],
            database=creds['eschol-db']['database'],
            cursorclass=cursor_class)
