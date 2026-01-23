from pub_oapi_tools_common.misc import log
import boto3
import json


def get_parameters(param_req: dict,
                   verbose: bool = True,
                   quiet: bool = False) -> dict:
    """
    Connects to AWS lambda to retrieve the specified params.
    It expects python dict input in the following formats

    {
        "name_of_thing_1": {
            "Folder": "path-to-thing-2",
        },
        "name_of_thing_2": {
            "Folder": "path-to-thing-1",
            "env": "qa"
        },
        "name_of_thing_3": {
            "Folder": "path-to-thing-3",
            "env": "prod"
            "names": ['name_1', 'name_2']
        },
        "name_of_thing_4": {
            "paths": ['/full/path/name_1', '/full/path/name_2']
        }
    }

    - The first retrieves all params in the path: path-to-think-1/*
    - The second retrieves all params in the path: path-to-thing-2/qa/*
    - The third retrieves only params listed in 'names' in: path-to-thing-3/prod
    - (The third pattern can be used with or without an 'env'.)
    - The fourth retrieves params from the provided paths

    :param param_req: See above for expected dict format.
    :param verbose: Prints extra debug info.
    :param quiet: Suppresses non-error logging output
    :return: A dict formatted like
        {name_of_thing_1: [{name_A: val_A, name_B: val_B}], ...}
    """

    if not quiet:
        log("INFO", __name__, "Retrieving parameters from AWS.")

    # Session and client setup
    session = boto3.session.Session()
    lambda_client = session.client('lambda', region_name='us-west-2')
    function_name = 'pub-oapi-tools-parameter-interface'

    try:
        if verbose and not quiet:
            log("DEBUG", __name__, f"input payload:\n{param_req}")

        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(param_req))

    except Exception as e:
        raise f"Error invoking Lambda function: {e}"

    params = validate_parameters_response(response, verbose, quiet)

    return params


def validate_parameters_response(raw_response, verbose, quiet):
    """
    Ensures 200 responses and checks for common problems.
    """

    if verbose and not quiet:
        log("DEBUG", __name__, f"Raw response:\n{raw_response}")

    # Check metadata HTTP status code
    metadata = raw_response['ResponseMetadata']
    if metadata['HTTPStatusCode'] != 200:
        log("ERROR", __name__,
            f"HTTP response from Lambda returned non-200:\n{metadata}")

    # Convert full response JSON string to dict
    response_payload = json.loads(raw_response['Payload'].read())
    if response_payload['statusCode'] < 199 or response_payload['statusCode'] > 299:
        log("ERROR", __name__,
            f"Lambda function returned a non-2XX response:\n{response_payload}")

    # Convert parameters sub-response JSON string to dict
    params_response = json.loads(response_payload['response'])

    if verbose and not quiet:
        log("DEBUG", __name__, f"params response:\n{params_response}")

    if not params_response or params_response == []:
        log("ERROR", __name__,
            (f"Lambda returned 200, but parameters were empty. "
             "This will likely cause runtime issues. "
             "Check your input folder/env against Parameter Store for typos."))

    for key, value in params_response.items():
        if verbose and not quiet:
            log("DEBUG", __name__, f"{key} : {value}")

        if not value or value == []:
            log("ERROR", __name__,
                (f'The parameters for {key} returned empty. '
                 'This will likely cause runtime issues. '
                 'Check your input folder/env against Parameter Store for typos.'))

    return params_response
