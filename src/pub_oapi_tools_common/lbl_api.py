from pub_oapi_tools_common.misc import log, output_dict_list_to_csv
from pub_oapi_tools_common import aws_lambda
import requests


def get_feed(output_to_filename: str = None):
    """
    Gets the LBL HR feed
    :param output_to_filename: Optional. If included, will output to CSV.
    :return: A list of dicts contianing information from the LBL HR feed.
    """
    param_req = {
        "lbl-hr-feed": {
            "folder": "pub-oapi-tools/lbl-api",
            "names": ['endpoint', 'client-id', 'client-secret']}}
    creds = aws_lambda.get_parameters(param_req=param_req, verbose=False)
    creds = creds['lbl-hr-feed']

    log("INFO", __name__, "Querying LBL feed for data.")

    result = requests.get(
        creds['endpoint'],
        stream=True,
        headers={'CF-Access-Client-Id': creds['client-id'],
                 'CF-Access-Client-Secret': creds['client-secret']})
    result_json = result.json()

    if output_to_filename:
        output_dict_list_to_csv(dict_list=result_json,
                                output_file_path=output_to_filename)

    return result_json
