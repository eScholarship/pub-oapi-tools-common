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
