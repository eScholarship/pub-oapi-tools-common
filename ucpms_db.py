"""
This program connects to the UCPMS datbase.

As of 2026-01-01, This is the Elements reporting database.
Please note that additional work is required from Symplectic
to allow this connection to occur (e.g. allow-listing IP CIDRs).
"""

import pyodbc
from misc import log


def get_connection(creds, autocommit=True, verbose=False):
    log("INFO", __name__,
        f"Connecting to the Elements reporting DB, database: {creds['database']}")
    log("INFO", __name__,
        f"This module uses the package pyodbc: https://pypi.org/project/pyodbc/")

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
