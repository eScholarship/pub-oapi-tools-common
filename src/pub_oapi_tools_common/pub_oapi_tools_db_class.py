"""
Functions for working with the pub-oapi-tools MySQL DB
"""

from pub_oapi_tools_common.misc import log
from pub_oapi_tools_common.misc import validate_creds
import pymysql


class PubOapiToolsDb:

    def __init__(self,
                 env: str = None,
                 database: str = None,
                 creds: dict = None,
                 cursor_class: str = "DictCursor",
                 quiet: bool = False,
                 verbose: bool = False):
        """
        An interface for working with OSTI's E-Link API 2.0.
        Must provide either an env string or a creds dict.

        :param creds: A dict containing driver, server, database, user, and password key/values.
        :param env: Presently, "prod" is the only env here.
        :param database: Name of the DB to connect to.
        :param cursor_class: (String) name of a PyMySQL cursor class:
            Cursor, DictCursor (default), SSCursor, or SSDictCursor. See here
            https://pymysql.readthedocs.io/en/latest/modules/cursors.html#
        :param quiet: Suppresses non-error logging output.
        :param verbose: Prints extra debug info.
        """

        # Set logging tags
        self.quiet = quiet
        self.verbose = verbose

        if not quiet:
            log("INFO", __name__,
                (f"Connecting to pub-oapi-tools RDS. "
                 f"This module uses the package pymysql: "
                 f"https://pymysql.readthedocs.io/en/latest/"))

        # Check for env or creds
        if not creds or (env and database):
            log("ERROR", __name__,
                ("Must provide either 'creds', or 'env' and 'database'. "
                 "Otherwise, we don't know what you want to connect to."))

        # If creds supplied, validate them
        elif creds:
            validation_keys = ['server', 'user', 'password', 'database']
            validate_creds(creds=creds, validation_keys=validation_keys)

        # If env supplied, connect to lambda for creds
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
            lambda_response = aws_lambda.get_parameters(
                param_req=param_req,
                quiet=self.quiet,
                verbose=self.verbose)
            creds = lambda_response['tools-rds']
            creds['database'] = lambda_response['tools-database'][database]

        # Set creds
        self.creds = creds

        # Set cursor class and establish connection
        # We typically use DictCursor, but other classes are available.
        # https://pymysql.readthedocs.io/en/latest/modules/cursors.html#
        if cursor_class == "DictCursor":
            self.cursor_class = pymysql.cursors.DictCursor
        elif cursor_class == "Cursor":
            self.cursor_class = pymysql.cursors.Cursor
        elif cursor_class == "SSCursor":
            self.cursor_class = pymysql.cursors.SSCursor
        elif cursor_class == "SSDictCursor":
            self.cursor_class = pymysql.cursors.SSDictCursor

        self.connection = self.connect()

    def connect(self) -> pymysql.connect:
        """
        Establishes and returns a connection to the pub-oapi-tools RDS instance
        :return: a pymysql connection object
        """
        return pymysql.connect(
            host=self.creds['server'],
            user=self.creds['user'],
            password=self.creds['password'],
            database=self.creds['database'],
            cursorclass=self.cursor_class)

    def get_connection(self) -> pymysql.connect:
        """
        Returns the pymysql connection object.
        :return: pymysql.connect object
        """
        return self.connection

    def close(self):
        """
        Closes the pymysql connection.
        """
        if self.connection.open:
            self.connection.close()

    def quick_execute(self,
                      query: str,
                      fetch: str = 'all'):
        """
        Executes a single query and returns the results.

        :param query: The SQL query in string format
        :param fetch: 'all' returns all records, otherwise a single record is returned.
        :return: A list of dicts if fetching all, or a single dict if fetching one.
        """

        # If the connection's closed, establish a new one.
        if not self.connection.open:
            self.connection = self.connect()

        # Open a cursor and send the query
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            if fetch == 'all':
                results = cursor.fetchall()
            else:
                results = cursor.fetchone()

        return results
