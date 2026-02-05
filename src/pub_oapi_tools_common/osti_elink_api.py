"""
Functions for connecting to OSTI's E-Link API.
OSTI E-Link 2 documentation https://osti.gov/elink2api/
"""
from pub_oapi_tools_common.misc import log
from pub_oapi_tools_common.misc import validate_creds

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from typing import Union


class ElinkApi:
    def __init__(self,
                 env: str = None,
                 creds: dict = None,
                 quiet: bool = False,
                 verbose: bool = False):
        """
        An interface for working with OSTI's E-Link API 2.0.
        Must provide either an env string or a creds dict.

        :param env: Name of the environment to use. (typically 'prod' or 'qa')
        :param creds: A dict containing key/value pairs.
        :param quiet: Suppresses non-error logging output.
        :param verbose: Prints extra debug info.
        """

        # Check for env or creds
        if not (env or creds):
            log("ERROR", __name__, "Must provide either env or creds.")

        # If creds supplied, validate
        elif creds:
            validation_keys = ['endpoint', 'token', 'pdf-user-agent']
            validate_creds(creds=creds, validation_keys=validation_keys)

        # If env supplied, connect to lambda for creds
        else:
            from pub_oapi_tools_common import aws_lambda
            param_req = {
                'osti_api': {
                    'folder': 'pub-oapi-tools/elink-api',
                    'env': env,
                    'names': ['endpoint', 'token', 'pdf-user-agent']}}
            creds = aws_lambda.get_parameters(param_req=param_req)
            creds = creds['osti_api']

        self.creds = creds
        self.quiet = quiet
        self.verbose = verbose

    def get_auth_header(self):
        """
        :return: Dict with auth and bearer token for Requests
        """
        return {'Authorization': f"Bearer {self.creds['token']}"}

    def post_metadata(self,
                      pub: dict = None,
                      submission_dict: dict = None
                      ) -> requests.Response:
        """
        Sends a POST request to E-Link's "Records" endpoint

        :param pub: Python dict of a pub object.
        :param submission_dict: Dict
        :return: A requests response object
        """
        if not (pub or submission_dict):
            log("ERROR", __name__,
                "Must supply either pub or submission dict.")
        else:
            submission = submission_dict if submission_dict \
                else submission = pub['submission_json']

        req_url = f"{self.creds['endpoint']}/records/submit"
        headers = self.get_auth_header()
        response = requests.post(req_url,
                                 json=submission,
                                 headers=headers)
        return response

    def put_metadata(self, pub) -> requests.Response:
        req_url = f"{self.creds['endpoint']}/records/{pub['osti_id']}/submit"
        headers = self.get_auth_header()
        response = requests.put(
            req_url, json=pub['submission_json'], headers=headers)
        return response

    def post_media(self, pub) -> requests.Response:
        req_url = f"{self.creds['endpoint']}/media/{pub['osti_id']}"

        # Get the PDF file data from url
        pdf_filename = pub['File URL'].split('/')[-1]
        pdf_headers = {'user-agent': self.creds['pdf-user-agent']}

        pdf_response = requests.get(
            pub['File URL'], headers=pdf_headers, stream=True)
        pdf_response.raw.decode_content = True

        mp_encoder = MultipartEncoder(
            fields={'file': (pdf_filename, pdf_response.content, 'application/pdf')})

        headers = self.get_auth_header()
        headers['Content-Type'] = mp_encoder.content_type
        params = {'title': pub['title']}

        # Send the post with the PDF data
        media_response = requests.post(
            req_url, headers=headers, params=params, data=mp_encoder)

        return media_response

    def put_media(self, pub) -> requests.Response:
        req_url = f"{self.creds['endpoint']}/media/{pub['osti_id']}/{pub['media_id']}"

        # Get the PDF file data from url
        pdf_filename = pub['File URL'].split('/')[-1]
        pdf_headers = {'user-agent': self.creds['pdf-user-agent']}

        pdf_response = requests.get(
            pub['File URL'],
            headers=pdf_headers,
            stream=True)
        pdf_response.raw.decode_content = True

        mp_encoder = MultipartEncoder(
            fields={'file': (pdf_filename, pdf_response.content, 'application/pdf')})

        headers = {'Authorization': 'Bearer ' + self.creds['token'],
                   'Content-Type': mp_encoder.content_type}
        params = {'title': pub['title']}

        # Send the post with the PDF data
        media_response = requests.put(
            req_url, headers=headers, params=params, data=mp_encoder)

        return media_response

    # ----------------------------------------
    # Functions for analytics work
    # E-Link API params documentation:
    # https://www.osti.gov/elink2api/#tag/records/operation/getRecords
    def get_pubs_by_workflow_status(self, workflow_status) -> requests.Response:
        req_url = f"{self.creds['endpoint']}/records"
        headers = self.get_auth_header()
        params = {
            'site_ownership_code': 'LBNLSCH',
            'date_first_submitted_from': '10/01/2024',
            'workflow_status': workflow_status}

        response = requests.get(
            req_url, params=params, headers=headers)
        return response

    def get_hidden_pubs(self) -> requests.Response:
        req_url = f"{self.creds['endpoint']}/records"
        headers = self.get_auth_header()
        params = {
            'site_ownership_code': 'LBNLSCH',
            'date_first_submitted_from': '10/01/2024',
            'hidden_flag': 'true'}

        response = requests.get(
            req_url, params=params, headers=headers)
        return response

    def get_single_pub(self, osti_id) -> requests.Response:
        req_url = f"{self.creds['endpoint']}/records/{osti_id}"
        headers = self.get_auth_header()
        response = requests.get(req_url, headers=headers)
        return response

    # Generic search function
    def search_metadata(self,
                        query_params: dict
                        ) -> requests.Response:
        """
        Search the OSTI E-Link metadata records.

        :param query_params: A dict containing the key/values for searching records.
            See the OSTI documentation here for a full list of params:
            https://www.osti.gov/elink2api/#tag/records/operation/getRecords
        :return: A Requests response object
        """

        if not self.quiet:
            log("INFO", __name__,
                "Sending metadata search request to E-Link 2 API")

        req_url = f"{self.creds['endpoint']}/records"
        headers = self.get_auth_header()
        response = requests.get(
            req_url, params=query_params, headers=headers)
        return response

    def get_comments(self,
                     osti_id: Union[int, str],
                     decode_json: bool = False
                     ) -> Union[requests.Response, None]:
        """
        Gets the OSTI comments for a single pub.

        :param osti_id: OSTI ID of the pub
        :param decode_json: if True, will return the result of
            response.json(). (Will halt on decoding error.)
        :return: If decode_json is False, returns a requests.Response object.
            NOTE! Response bodies can be encoded in a variety of
            different ways. Some requests decoding methods raise
            exceptions if called on content of the wrong format.
            See here for details:
            https://requests.readthedocs.io/en/latest/api/#requests.Response
        """

        if not self.quiet:
            log("INFO", __name__,
                f"Sending comments search request to E-Link 2 API, OSTI ID {osti_id}")

        req_url = f"{self.creds['endpoint']}/comments/{osti_id}"
        headers = self.get_auth_header()
        response = requests.get(req_url, headers=headers)
        if decode_json:
            try:
                return_json = response.json()
                return return_json
            except requests.exceptions.JSONDecodeError as e:
                log("WARN", __name__,
                    "JSONDecodeError while decoding the response. Returning None")
                return None
        else:
            return response
