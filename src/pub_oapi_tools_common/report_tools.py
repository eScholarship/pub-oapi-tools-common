from pub_oapi_tools_common import aws_lambda
import subprocess


def get_email_addresses(emails: list):
    """
    Returns email addresses for the names specified in the email list.

    :param emails: The 'emails' list from the report_dict.
        These refer to addresses in AWS param store
    :return: A list of email addresses
    """

    param_req = {
        'emails': {
            'folder': 'pub-oapi-tools/emails',
            'names': emails}
    }

    email_params = aws_lambda.get_parameters(param_req=param_req)
    emails = list(email_params['emails'].values())
    return emails


def send_emails(report_dict, email_addresses):
    """
    Puts together the required format for running the mail subprocess.

    :param report_dict: Info abt the report specified via the args
    :param email_addresses: An array of email addresses
    """

    subprocess_setup = ['mail', '-s', report_dict['email_subject']]

    for file in report_dict['attachment_files']:
        subprocess_setup += ['-a', file]

    subprocess_setup += email_addresses

    email_footer = b"\n\nThis is an automated email sent from the pub-oapi-tools EC2. " \
                   b"Repo: https://github.com/eScholarship/report-runner" \
                   b"\n\nRemember to stay hydrated and get plenty of rest!"

    email_body = report_dict['email_body'] + email_footer

    print("Running mail subprocess.")
    subprocess.run(subprocess_setup,
                   input=email_body,
                   capture_output=True)
