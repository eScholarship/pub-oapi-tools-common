"""
Functions for working with the eScholarship analytics
MySQL DB. Note that the host of this DB will change
every time a new analytics replica is spun up.
"""

import pymysql
from pub_oapi_tools_common.misc import log


def get_connection(creds: dict = None,
                   env: str = None,
                   database: str = None,
                   cursor_class: str = "DictCursor",
                   quiet: bool = False
                   ) -> pymysql.connections.Connection:
    """
    Connects to an analytics copy of the eScholarship MySQL db.

    Usage:
        get_connection(creds) -- see aws_lambda.py for expected dict input format
        or get_connection(env, database)

    :param creds: A dict containing driver, server, database, user, and password key/values.
    :param env: Presently, "prod" is the only env here.
    :param database: Name of the DB to connect to.
    :param cursor_class: (String) name of a PyMySQL cursor class:
        Cursor, DictCursor (default), SSCursor, or SSDictCursor. See here
        https://pymysql.readthedocs.io/en/latest/modules/cursors.html#
    :param quiet: Suppresses non-error logging output
    :return: An open PyMySQL connection.
    """

    if not quiet:
        log("INFO", __name__,
            (f"Connecting to ephemeral eScholarship analytics database. "
             f"This module uses the package pymysql: "
             f"https://pymysql.readthedocs.io/en/latest/"))

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
        from pub_oapi_tools_common import aws_lambda

        param_req = {
            'eschol-analytics': {
                'folder': 'pub-oapi-tools/eschol-analytics'}}

        creds = aws_lambda.get_parameters(
            param_req=param_req,
            quiet=quiet)

        return pymysql.connect(
            host=creds['eschol-analytics']['server'],
            user=creds['eschol-analytics']['user'],
            password=creds['eschol-analytics']['password'],
            database=creds['eschol-analytics']['database'],
            cursorclass=cursor_class)
