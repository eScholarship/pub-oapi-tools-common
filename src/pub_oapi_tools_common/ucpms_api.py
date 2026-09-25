from pub_oapi_tools_common.misc import log, validate_creds
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
                ("Must provide either 'creds', or 'env'. "
                 "Otherwise, we don't know what you want to connect to."))

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

        log("INFO", __name__,
            f"Sending: {http_method} to {self.creds['endpoint']}/{query_path}")

        try:
            if http_method == 'GET':
                response = self.get(endpoint=self.creds['endpoint'],
                                    query_path=query_path,
                                    body_xml=body_xml)
            elif http_method == 'PUT':
                response = self.put(endpoint=self.creds['endpoint'],
                                    query_path=query_path,
                                    body_xml=body_xml)
            elif http_method == 'PATCH':
                response = self.patch(endpoint=self.creds['endpoint'],
                                      query_path=query_path,
                                      body_xml=body_xml)
            else:
                log("ERROR", __name__,
                    f"Specified HTTP method {http_method} not supported.")
        except requests.exceptions.ConnectionError:
            log("ERROR", __name__,
                f"The internet connection was lost or the server is down.")
        except requests.exceptions.Timeout:
            log("ERROR", __name__,
                f"The request timed out.")
        except requests.exceptions.RequestException as e:
            log("ERROR", __name__,
                f"An unexpected error occurred: {e}")

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

    def get(self,
            endpoint: str,
            query_path: str,
            body_xml: str = None) -> requests.Response:

        req_url = f"{endpoint}/{query_path}"
        headers = {"Content-Type": "application/xml"} \
            if body_xml else None

        response = requests.get(req_url,
                                auth=self.auth,
                                headers=headers,
                                data=body_xml)

        return response

    def put(self,
            endpoint: str,
            query_path: str,
            body_xml: str = None) -> requests.Response:

        req_url = f"{endpoint}/{query_path}"

        headers = {"Content-Type": "application/xml"} \
            if body_xml else None

        response = requests.put(req_url,
                                auth=self.auth,
                                headers=headers,
                                data=body_xml)
        return response

    def patch(self,
              endpoint: str,
              query_path: str,
              body_xml: str = None) -> requests.Response:

        req_url = f"{endpoint}/{query_path}"
        headers = {"Content-Type": "application/xml"} \
            if body_xml else None

        response = requests.patch(req_url,
                                  auth=self.auth,
                                  headers=headers,
                                  data=body_xml,
                                  timeout=10)

        return response
