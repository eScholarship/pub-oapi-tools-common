"""
This module contains small helper functions.
"""


class Colors:
    """ Codes for bash text colors """
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'  # Resets the color


def log(level: str,
        module: str,
        message: str):
    """
    Prints messages standard machine-readable format:
        [timestamp] [level] [module] message

    "ERROR" or "FATAL" levels will exit(1) after printing.

    :param level: Use the following standard-issue levels for readability, INFO, DEBUG, TRACE, WARN, ERROR, FATAL.
    :param module: The name of the module printing the log. (Typically, use __name__ here.)
    :param message: The log text.
    """

    from pub_oapi_tools_common.misc import Colors
    from datetime import datetime

    now = datetime.now().isoformat()[:-3]
    if level == "ERROR" or level == "FATAL":
        print(f"[{Colors.CYAN}{now}{Colors.RESET}] "
              f"[{Colors.RED}{level}{Colors.RESET}] "
              f"[{module}] {message}")
        exit(1)

    else:
        level_color = Colors.GREEN if level == "INFO" else Colors.YELLOW
        print(f"[{Colors.CYAN}{now}{Colors.RESET}] "
              f"[{level_color}{level}{Colors.RESET}] "
              f"[{Colors.MAGENTA}{module}{Colors.RESET}] "
              f"{message}")


def output_dict_list_to_csv(dict_list: list,
                            output_file_path: str):
    """
    Outputs a list of dicts to CSV.
    Typically used for saving results of SQL queries.

    :param dict_list: A list of python dicts
    :param output_file_path: The destination file (path and name).
        If no path is provided, the file outputs to the current working dir.
    :return:
    """

    import csv

    with open(output_file_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(dict_list[0].keys())  # CSV header
        for row in dict_list:
            csv_writer.writerow(row.values())


def validate_creds(creds: dict,
                   validation_keys=list,
                   check_values=True) -> bool:
    """
    Checks to make sure certain keys are present in a creds dict,
    and unless otherwise specified, that values for these keys
    are present.

    :param creds: A dict with key/value pairs
    :param validation_keys: A list of keys to check for.
    :param check_values: Ensure values for validation keys are present.
    :return: Returns True if creds are valid, otherwise, will
        exit with an error indicating the problem.
    """

    for v_k in validation_keys:
        if v_k not in creds.keys():
            log("ERROR", __name__,
                f"Your creds file is missing a required key: {validation_keys}")
        if check_values and (creds[v_k] is None or creds[v_k] == ""):
            log("ERROR", __name__,
                f"Your creds dict contains an empty value for the key: {validation_keys}. "
                f"(To skip value checks during validation, run with check_values=False).")

    return True


def requests_error_handling(func):
    """
    Decorator for wrapping requests functions like
    .get(), .put(), and .patch() in error handling
    :param func: The requests function to wrap
    :return: Results from the requests function
    """

    import requests

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as http_err:
            log("ERROR", __name__, f"4xx/5xx response: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            log("ERROR", __name__, f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            log("ERROR", __name__, f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as err:
            log("ERROR", __name__, f"An unexpected requests error occurred: {err}")
        except Exception as e:
            log("ERROR", __name__, f"An unexpected non-requests error occurred: {e}")

    return wrapper


def chunk_list_to_size_n(list_to_chunk, chunk_size):
    """
    Chunk a list into lists of size n.
    :param list_to_chunk: The original (flat) list
    :param chunk_size: The size of the sublists
    :return: A list of lists
    """
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    return list(chunks(list_to_chunk, chunk_size))
