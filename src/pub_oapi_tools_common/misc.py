"""
This module contains small helper functions.
"""


def log(level: str,
        module: str,
        message: str):
    """
    Prints messages standard machine-readable format:
    [timestamp] [level] [module] [message]
    "ERROR" or "FATAL" levels will raise() instead of print().

    :param level: Use the following standard-issue levels for readability, INFO, DEBUG, TRACE, WARN, ERROR, FATAL.
    :param module: The name of the module printing the log. (Typically, use __name__ here.)
    :param message: The log text.
    """

    class Colors:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        RESET = '\033[0m'  # Resets the color

    from datetime import datetime

    now = datetime.now().isoformat()
    if level == "ERROR" or level == "FATAL":
        raise f"{Colors.CYAN}[{now}]{Colors.RESET} " \
              f"{Colors.RED}[{level}]{Colors.RESET} " \
              f"[{module}] {message}"
    else:
        print(f"{Colors.CYAN}[{now}]{Colors.RESET} "
              f"{Colors.GREEN}[{level}]{Colors.RESET} "
              f"[{module}] {message}")
