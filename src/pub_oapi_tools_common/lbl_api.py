from pub_oapi_tools_common.misc import log
from pub_oapi_tools_common.misc import output_dict_list_to_csv
from pub_oapi_tools_common.misc import requests_error_handling
from pub_oapi_tools_common import aws_lambda
import requests


def get_feed(quiet: bool = False,
             output_to_filename: str = None):
    """
    Gets the LBL HR feed
    :param quiet: Suppresses non-error logging output.
    :param output_to_filename: Optional. If included, will output to CSV.
    :return: A list of dicts containing data from the LBL HR feed.
    """
    param_req = {
        "lbl-hr-feed": {
            "folder": "pub-oapi-tools/lbl-api",
            "names": ['endpoint', 'client-id', 'client-secret']}}

    creds = aws_lambda.get_parameters(param_req=param_req,
                                      verbose=False)

    creds = creds['lbl-hr-feed']

    if not quiet:
        log("INFO", __name__, "Querying LBL feed for data.")

    @requests_error_handling
    def requests_get():
        req_result = requests.get(
            creds['endpoint'],
            stream=True,
            headers={'CF-Access-Client-Id': creds['client-id'],
                     'CF-Access-Client-Secret': creds['client-secret']})
        return req_result

    result = requests_get()
    result_json = result.json()

    if output_to_filename:
        if not quiet:
            log("INFO", __name__, f"Saving feed results to file: {output_to_filename}")
        output_dict_list_to_csv(dict_list=result_json,
                                output_file_path=output_to_filename)

    return result_json
