from pub_oapi_tools_common.misc import log
import boto3


def get_logs_client(quiet: bool = False
                    ) -> boto3.session.Session().client:
    """
    Gets a cloudwatch logs client from AWS.
    :param quiet: Suppresses non-error logging output
    :return: A boto3 cloudwatch logs client
    """

    if not quiet:
        log("INFO", __name__, "Retrieving the cloudwatch logs client from AWS.")

    session = boto3.session.Session()
    logs_client = session.client(service_name='logs',
                                 region_name='us-west-2')

    return logs_client


def put_logs(log_group: str,
             log_stream: str,
             log_events: list,
             logs_client: boto3.session.Session().client = None,
             verbose: bool = False,
             quiet: bool = False):
    """
    Adds log events to a CloudWatch log stream.

    :param log_group: Name of the log group
    :param log_stream: Name of the log stream
    :param log_events: A list of python dicts in the AWS format
        [{'timestamp':<ts>, 'message': <string>}, {}, ...]
    :param logs_client: If you've already gotten a logs client (e.g. for reading logs),
        you can provide it here. Otherwise, this will create a new one.
    :param verbose: Prints extra debug info.
    :param quiet: Suppresses non-error logging output
    """

    if not quiet:
        log("INFO", __name__, "Uploading cloudwatch log events.")

    if not logs_client:
        logs_client = get_logs_client(quiet=quiet)

    response = logs_client.put_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        logEvents=log_events)

    if verbose and not quiet:
        log("DEBUG", __name__, response)
