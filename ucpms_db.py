"""
Functions for working with the UCPMS reporting DB.

As of 2026-01-01, This is the Elements reporting database.
Please note that additional work is required from Symplectic
to allow this connection to occur (e.g. allow-listing IP CIDRs).
"""

import pyodbc
from misc import log


def get_connection(creds=None, env=None, autocommit=True, verbose=False):
    """
    Connects to the Elements reporting DB.

    Usage:
        get_connection(creds) -- see aws_lambda.py for expected dict input format
        or get_connection(env, database)

    Returns an open pyodbc connection
    """

    log("INFO", __name__,
        (f"Connecting to the Elements reporting DB. "
         f"This module uses the package pyodbc: https://pypi.org/project/pyodbc/"))

    if not (creds or env):
        log("ERROR", __name__,
            ("Must provide either 'creds', or 'env'. "
             "Otherwise, we don't know what you want to connect to."))

    # User has supplied creds from parameter store
    if creds:
        mssql_conn = pyodbc.connect(
            driver=creds['driver'],
            server=(creds['server'] + ',1433'),
            database=creds['database'],
            uid=creds['user'],
            pwd=creds['password'],
            trustservercertificate='yes')

    # User supplied env and db name. Connect to lambda for creds
    else:
        from aws_lambda import get_parameters
        creds = {
            'elements_db': {
                'folder': 'pub-oapi-tools/elements-reporting-db',
                'env': env}}
        creds = get_parameters(creds)['elements_db']

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
