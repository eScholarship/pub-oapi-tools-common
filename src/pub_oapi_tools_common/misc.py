"""
This module contains small helper functions.
"""


def log(level: str, module: str, message: str):
    """
    Prints messages standard machine-readable format:
    [timestamp] [level] [module] [message]
    "ERROR" or "FATAL" levels will raise() instead of print().

    :param level: Use the following standard-issue levels for readability, INFO, DEBUG, TRACE, WARN, ERROR, FATAL.
    :param module: The name of the module printing the log. (Typically, use __name__ here.)
    :param message: The log text.
    """

    from datetime import datetime

    now = datetime.now().isoformat()
    if level == "ERROR" or level == "FATAL":
        raise f"[{now}] [{level}] [{module}] {message}"
    else:
        print(f"[{now}] [{level}] [{module}] {message}")
