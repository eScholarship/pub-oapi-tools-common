"""
Functions for working with the UCPMS reporting DB.

As of 2026-01-01, This is the Elements reporting database.
Please note that additional work is required from Symplectic
to allow this connection to occur (e.g. allow-listing IP CIDRs).
"""

from pub_oapi_tools_common.misc import log
import pyodbc


def get_connection(creds: dict = None,
                   env: str = None,
                   autocommit: bool = True,
                   quiet: bool = False,
                   verbose: bool = False) -> pyodbc.Connection:
    """
    Connects to the Elements reporting DB. Requires either a creds JSON
    or an env variable (prod or qa). Uses the pyodbc package.

    :param creds: A dict containing keys/values for:
        driver, server, database, user, and password.
    :param env: "prod" or "qa".
    :param autocommit: "True" required for queries that use transactions.
    :param verbose: Prints extra debug info.
    :param quiet: Suppresses non-error logging output.
    :return: An open pyodbc connection
    """

    if not quiet:
        log("INFO", __name__,
            (f"Connecting to the Elements reporting DB. "
             f"This module uses the package pyodbc: https://pypi.org/project/pyodbc/"))

    if not (creds or env):
        log("ERROR", __name__,
            ("Must provide either 'creds', or 'env'. "
             "Otherwise, we don't know what you want to connect to."))

    # If user supplies only the env, get the creds from Lambda.
    if not creds:
        from pub_oapi_tools_common import aws_lambda
        param_req = {
            'elements_db': {
                'folder': 'pub-oapi-tools/elements-reporting-db',
                'env': env}}
        creds = aws_lambda.get_parameters(param_req=param_req)
        creds = creds['elements_db']

    mssql_conn = pyodbc.connect(
        driver=creds['driver'],
        server=(creds['server'] + ',1433'),
        database=creds['database'],
        uid=creds['user'],
        pwd=creds['password'],
        trustservercertificate='yes')

    # Required when queries use TRANSACTION
    mssql_conn.autocommit = autocommit

    return mssql_conn


def get_dict_list(cursor: pyodbc.Cursor) -> list:
    """
    Converts PYODBC output to a list of dicts.
    Run this following `cursor.execute()`.

    :param cursor: A pyodbc cursor
    :return: A list of dicts
    """

    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return rows
