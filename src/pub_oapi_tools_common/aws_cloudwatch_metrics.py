from pub_oapi_tools_common.misc import log
import boto3
from datetime import datetime


def get_logs_client(quiet: bool = False,
                    verbose: bool = False
                    ) -> boto3.session.Session().client:
    """
    Gets a cloudwatch client from AWS.
    (Typically used for sending metrics to AWS.)
    :param quiet: Suppresses non-error logging output
    :param verbose: Prints extra debug info.
    :return: A boto3 cloudwatch client
    """

    if not quiet:
        log("INFO", __name__, "Retrieving the cloudwatch client from AWS.")

    session = boto3.session.Session()

    cloudwatch_client = session.client(service_name='cloudwatch',
                                       region_name='us-west-2')

    return cloudwatch_client


def put_metrics(namespace: str,
                metrics_data: list,
                client: boto3.client = get_logs_client(),
                quiet: bool = False
                ):
    """
    Uploads metric data to CloudWatch.
    The metrics_data input must be a list of AWS'
    MetricData objects, see here:
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/put_metric_data.html
    - https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_MetricDatum.html

    :param namespace: The CW Metrics namespace for the metrics
    :param metrics_data: A list of MetricsDatum (see above)
    :param client: A boto3 Cloudwatch client.
        If blank, a new client is gotten.
    :param quiet: Suppresses non-error logging output.
    :return: A response object
    """

    response = client.put_metric_data(
        MetricData=metrics_data,
        Namespace=namespace)

    if not quiet:
        print(response)

    return response
