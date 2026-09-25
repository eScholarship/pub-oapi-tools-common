"""
Functions for working with the eScholarship MySQL DB
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
    Connects to the eScholarship MySQL database.

    Usage:
        get_connection(creds) -- see aws_lambda.py for expected dict input format
        or get_connection(env, database)

    :param creds: A dict containing driver, server, database, user, and password key/values.
    :param env: "prod" or "staging"
    :param database: Name of the DB to connect to.
    :param cursor_class: (String) name of a PyMySQL cursor class:
        Cursor, DictCursor (default), SSCursor, or SSDictCursor. See here
        https://pymysql.readthedocs.io/en/latest/modules/cursors.html#
    :param quiet: Suppresses non-error logging output
    :return: An open PyMySQL connection.
    """

    if not quiet:
        log("INFO", __name__,
            (f"Connecting to eScholarship database. "
             f"This module uses the package pymysql: "
             f"https://pymysql.readthedocs.io/en/latest/"))

    if not (creds or (env and database)):
        raise ValueError("Must provide either 'creds', or 'env' and 'database'. "
                         "Otherwise, we don't know what you want to connect to.")

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
            'eschol-db': {
                'folder': 'pub-oapi-tools/eschol-db',
                'env': env}}

        creds = aws_lambda.get_parameters(
            param_req=param_req,
            quiet=quiet)

        return pymysql.connect(
            host=creds['eschol-db']['server'],
            user=creds['eschol-db']['user'],
            password=creds['eschol-db']['password'],
            database=creds['eschol-db']['database'],
            cursorclass=cursor_class)


def quick_query(env: str, query: str):
    """
    Send a single query to the eSchol DB and returns a list of dicts.

    :param env: prod, qa, or dev.
    :param query: A string of the SQL query to send
    :return: A list of dicts of the query results
    """
    if not (env == 'prod' or env == 'qa' or env == 'dev'):
        log("ERROR", __name__, "Env value not prod or QA.")

    database = 'eschol' if env == 'prod' else 'eschol-test'

    conn = get_connection(env=env, database=database)

    with conn.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    conn.close()

    return results
