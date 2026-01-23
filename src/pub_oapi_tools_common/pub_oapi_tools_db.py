"""
Functions for working with the pub-oapi-tools MySQL DB
"""

from pub_oapi_tools_common.misc import log
import pymysql


def get_connection(creds: dict = None,
                   env: str = None,
                   database: str = None,
                   cursor_class: str = "DictCursor"
                   ) -> pymysql.connections.Connection:
    """
    Connects to the pub-oapi-tools RDS.

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
        (f"Connecting to pub-oapi-tools RDS. "
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

    # Using the env and/or database name,
    else:
        from pub_oapi_tools_common import aws_lambda

        param_req = {
            'tools-rds': {
                'folder': 'pub-oapi-tools/tools-rds',
                'env': env,
                'names': ['server', 'user', 'password']},
            'tools-database': {
                'folder': 'pub-oapi-tools/tools-rds',
                'env': env,
                'names': [database]}
        }
        creds = aws_lambda.get_parameters(param_req=param_req)

        return pymysql.connect(
            host=creds['tools-rds']['server'],
            user=creds['tools-rds']['user'],
            password=creds['tools-rds']['password'],
            database=creds['tools-database'][database],
            cursorclass=cursor_class)
