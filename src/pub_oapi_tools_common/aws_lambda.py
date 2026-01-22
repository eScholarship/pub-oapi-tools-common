from pub_oapi_tools_common.misc import log
import boto3
import json


def get_parameters(input_payload: dict,
                   verbose: bool = True) -> dict:
    """
    Connects to AWS lambda to retrieve the specified params.
    It expects python dict input in the following formats

    {
        "name_of_thing_1": {
            "Folder": "path-to-thing-1",
            "env": "qa"
        },
        "name_of_thing_2": {
            "Folder": "path-to-thing-2",
        },
        "name_of_thing_3": {
            "Folder": "path-to-thing-3",
            "env": "prod"
            "names": ['name_1', 'name_2']
        },
    }

    - The first retrieves all params in the path: path-to-thing-1/qa/*
    - The second retrieves all params in the path: path-to-think-2/*
    - The third retrieves only params listed in 'names' in: path-to-thing-3/prod
    (The third pattern can also be used without an 'env'.)

    :param input_payload: See above for expected dict format.
    :param verbose: Prints extra debug info.
    :return: A dict formatted like {name_of_thing_1: [{name_A: val_A, name_B: val_B}], ...}
    """

    log("INFO", __name__, "Retrieving parameters from AWS.")

    # Session and client setup
    session = boto3.session.Session()
    lambda_client = session.client('lambda', region_name='us-west-2')
    function_name = 'pub-oapi-tools-parameter-interface'

    try:
        if verbose:
            log("DEBUG", __name__, f"input payload:\n{input_payload}")

        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(input_payload))

        params = validate_parameters_response(response, verbose)

    except Exception as e:
        raise f"Error invoking Lambda function: {e}"

    return params


def validate_parameters_response(raw_response, verbose):
    """
    Ensures 200 responses and checks for common problems.
    Called from get_parameters() above.
    """

    if verbose:
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

    if verbose:
        log("DEBUG", __name__, f"params response:\n{params_response}")

    if not params_response or params_response == []:
        log("ERROR", __name__,
            (f"Lambda returned 200, but parameters were empty. "
             "This will likely cause runtime issues. "
             "Check your input folder/env against Parameter Store for typos."))

    for key, value in params_response.items():
        if verbose:
            log("DEBUG", __name__, f"{key} : {value}")

        if not value or value == []:
            log("ERROR", __name__,
                (f'The parameters for {key} returned empty. '
                 'This will likely cause runtime issues. '
                 'Check your input folder/env against Parameter Store for typos.'))

    return params_response
