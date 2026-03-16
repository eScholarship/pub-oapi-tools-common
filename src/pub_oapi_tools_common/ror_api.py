from pub_oapi_tools_common.misc import log
from pub_oapi_tools_common.misc import validate_creds

from urllib.parse import quote
from pprint import pprint
from time import sleep
import requests


class RorApi:
    def __init__(self,
                 creds: dict = None,
                 quiet: bool = False,
                 verbose: bool = False):
        """
        An interface for working with the ROR api.
        Must provide either an env string or a creds dict.

        :param env: Name of the environment to use. (typically 'prod' or 'qa')
        :param creds: A dict containing key/value pairs.
        :param quiet: Suppresses non-error logging output.
        :param verbose: Prints extra debug info.
        """

        # If creds supplied, validate
        if creds:
            validation_keys = ['endpoint', 'client-id']
            validate_creds(creds=creds, validation_keys=validation_keys)

        # If env supplied, connect to lambda for creds
        else:
            from pub_oapi_tools_common import aws_lambda
            param_req = {
                'ror-api': {
                    'folder': 'pub-oapi-tools/ror-api'}}
            creds = aws_lambda.get_parameters(
                param_req=param_req)
            creds = creds['ror-api']

        self.creds = creds
        self.quiet = quiet
        self.verbose = verbose

    def get_auth_header(self):
        """
        :return: Dict with Client-Id for req header
        """
        return {'Client-Id': self.creds['client-id']}

    def test_req(self):
        headers = self.get_auth_header()
        req_url = f"{self.creds['endpoint']}/organizations"
        params = {'query': 'oxford'}

        response = requests.get(
            req_url, params=params, headers=headers)

        log("INFO", __name__, f"Req status code: {response.status_code}")
        log("INFO", __name__, f"Req body JSON: {response.json()}")

    def affiliation_search(self, affiliation_string):
        """
        Uses ROR's fuzzy affiliation matching to identify
        organizations from free text.

        Note: this API includes two searching strategies,
        single search and multi-search. The difference lies
        in whether the search string is divided into
        multiple tokens. The ROR documentation suggests the
        single search is a little more efficient and provides
        better results.

        :param affiliation_string: The affiliation string on which
            to search. This function handles the URL encoding if
            spaces or special characters appear in the string.
        """

        log("INFO", __name__, f"Searching: {affiliation_string}")

        headers = self.get_auth_header()
        req_url = f"{self.creds['endpoint']}/organizations"
        params = {'affiliation': quote(affiliation_string),
                  'single_search': None}

        response = requests.get(
            req_url, params=params, headers=headers)

        if 200 <= response.status_code <= 299:
            log("INFO", __name__, f"Req status code: {response.status_code}")
        elif response.status_code >= 500:
            log("ERROR", __name__, f"5XX response from ROR API")
        else:
            log("WARN", __name__, f"Non-200 status code: {response.status_code}")
            return None

        body = response.json()
        if self.verbose:
            log("INFO", __name__, f"Response body:")
            pprint(body)

        if self.verbose:
            for item in body['items']:
                org = item['organization']
                en_name = [i['value'] for i in org['names']
                           if i['lang'] == 'en']
                en_name = en_name[0] if en_name else None

                print(f"{item['chosen']} "
                      f"{item['score']} "
                      f"{org['domains']} "
                      f"{org['id']} "
                      f"{en_name}")

        if body['items']:
            return body['items']
        else:
            return None

#
# ror = RorApi()
# test_affils = [
#     "University of Bonn, Germany",
#     "University of Hohenheim, Germany",
#     "San Diego State University Department of Women’s Studies",
#     "Anderson School of Management",
#     "Research Institute of Pomology and Floriculture"]
#
# for affil in test_affils:
#     ror.affiliation_search(affil)
#     sleep(2)
