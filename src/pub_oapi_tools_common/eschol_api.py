from pub_oapi_tools_common.misc import log
import requests


def send_query(creds: dict = None,
               env: str = None,
               query: str = None,
               variables: dict = None,
               verbose: bool = False,
               quiet: bool = False) -> requests.Response:
    """
    Sends a request to the eSchol API.
    Requires either a creds dict or an env (prod or qa).
    Uses the requests package.

    :param creds: Must include endpoint, cookie, and priv-key
    :param env: specify 'prod' or 'qa'
    :param query: A json string
    :param variables: Python dicts is expected here, but stick to
        int and str, as it's likely more complex data types
        may cause problems.
    :param verbose: Prints extra debug info.
    :param quiet: Suppresses non-error logging output.
    :return: A Response object from requests. Useful fields
        of this object include: status_code, reason, text,
        json, encoding... etc. See here:
        https://requests.readthedocs.io/en/latest/api/#requests.Response
    """

    if not quiet:
        log("INFO", __name__,
            (f"Sending a query to the eSchol API. "
             f"This module uses the package requests: https://requests.readthedocs.io/en/latest/"))

    if not (creds or env):
        log("ERROR", __name__,
            ("Must provide either 'creds', or 'env'. "
             "Otherwise, we don't know what you want to connect to."))

    if not query:
        log("ERROR", __name__, "Must supply a query.")

    if '$' in query and not variables:
        log("WARN", __name__,
            ("Looks like you're sending a query that uses a $, "
             "but you haven't supplied a 'variables' parameter. "
             "Please ensure your variables are encoded correctly "
             "in the query itself."))

    # If user supplies only the env, get the creds from Lambda.
    if not creds:
        from pub_oapi_tools_common import aws_lambda
        param_req = {
            'eschol_api': {
                'folder': 'pub-oapi-tools/eschol-api',
                'env': env,
                'names': ['endpoint', 'priv-key', 'cookie']}}
        creds = aws_lambda.get_parameters(param_req=param_req)
        creds = creds['eschol_api']

    # Set headers and cookies
    headers = dict(PRIVILEGED=creds['priv-key'])
    cookies = dict(ACCESS_COOKIE=creds['cookie'])

    # Package the query and vars
    if variables:
        json = {'query': query,
                'variables': {'input': variables}}
    else:
        json = {'query': query}

    # Send the request
    response = requests.post(
        url=creds['endpoint'],
        headers=headers,
        cookies=cookies,
        json=json)

    if verbose:
        log("DEBUG", __name__, f"eSchol API response code: {response.status_code}")
        log("DEBUG", __name__, f"eSchol API response reason: {response.reason}")

    return response
