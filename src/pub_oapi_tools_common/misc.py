"""
This module contains small helper functions.
"""


def log(level, module, message):
    """
    Prints messages standard machine-readable format:
    [timestamp] [level] [module] [message]
    "ERROR"-level logs will raise() instead of print()

    :param level:
    :param module:
    :param message:
    :return:
    """

    from datetime import datetime

    now = datetime.now().isoformat()
    if level == "ERROR":
        raise f"[{now}] [{level}] [{module}] {message}"
    else:
        print(f"[{now}] [{level}] [{module}] {message}")
