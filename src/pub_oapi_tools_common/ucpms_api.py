from pub_oapi_tools_common.misc import log
from pub_oapi_tools_common.misc import validate_creds
from pub_oapi_tools_common.misc import requests_error_handling
import xml.etree.ElementTree as ET
import requests


class UCPMSApi:
    def __init__(self,
                 env: str = None,
                 creds: dict = None,
                 quiet: bool = False,
                 verbose: bool = False):

        if not (creds or env):
            log("ERROR", __name__,
                "Must provide either 'creds', or 'env'. "
                "Otherwise, we don't know what you want to connect to.")

        # If creds supplied, validate
        if creds:
            validation_keys = ['endpoint', 'username', 'password']
            validate_creds(creds=creds, validation_keys=validation_keys)

        # If env supplied, connect to lambda for creds
        else:
            from pub_oapi_tools_common import aws_lambda
            param_req = {
                'elements-api': {
                    'folder': 'pub-oapi-tools/elements-api',
                    'env': env}}
            creds = aws_lambda.get_parameters(param_req=param_req)
            creds = creds['elements-api']

        self.creds = creds
        self.quiet = quiet
        self.verbose = verbose
        self.auth = (self.creds['username'], self.creds['password'])

    def query(self,
              query_path: str,
              http_method: str = 'GET',
              body_xml: str = None,
              return_xml_tree: bool = False):
        """
        This main function dispatches the query to the specified
        endpoint with the specified http method.

        :param query_path: URL of the API operation
        :param http_method: GET, PUT, PATCH
        :param body_xml: Optional ElementTree XML body for the operation
        :param return_xml_tree: T/F, see below
        :return: If return_xml_tree is True, returns an ElementTree root.
            Otherwise, returns an XML string.
        """
        http_method = http_method.upper()

        req_url = f"{self.creds['endpoint']}/{query_path}"
        headers = {"Content-Type": "application/xml"} if body_xml else None

        log("INFO", __name__, f"Sending: {http_method} to {req_url}")

        if http_method == 'GET':
            response = self.get(req_url=req_url,
                                headers=headers,
                                body_xml=body_xml)

        elif http_method == 'PUT':
            response = self.put(req_url=req_url,
                                headers=headers,
                                body_xml=body_xml)

        elif http_method == 'PATCH':
            response = self.patch(req_url=req_url,
                                  headers=headers,
                                  body_xml=body_xml)
        else:
            log("ERROR", __name__,
                f"Specified HTTP method {http_method} not supported.")

        if not self.quiet:
            log("INFO", __name__,
                f"Response status code: {response.status_code}")

        if response.status_code >= 400:
            log("WARN", __name__,
                f"Response status code {response.status_code}, "
                f"unexpected behavior may occur.")

        xml_string = response.text

        if not return_xml_tree:
            return xml_string
        else:
            root = ET.fromstring(xml_string)
            return root

    @requests_error_handling
    def get(self,
            req_url: str,
            headers: dict = None,
            body_xml: str = None) -> requests.Response:

        response = requests.get(req_url,
                                auth=self.auth,
                                headers=headers,
                                data=body_xml)
        return response

    @requests_error_handling
    def put(self,
            req_url: str,
            headers: dict = None,
            body_xml: str = None) -> requests.Response:

        response = requests.put(req_url,
                                auth=self.auth,
                                headers=headers,
                                data=body_xml)
        return response

    @requests_error_handling
    def patch(self,
              req_url: str,
              headers: dict = None,
              body_xml: str = None) -> requests.Response:

        response = requests.patch(req_url,
                                  auth=self.auth,
                                  headers=headers,
                                  data=body_xml)
        return response
