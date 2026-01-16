"""
This module contains small helper functions.
"""


# Prints messages standard machine-readable format.
# "ERROR"-level logs will raise & exit
def log(level, module, text):
    from datetime import datetime

    now = datetime.now().isoformat()
    if level == "ERROR":
        raise f"[{now}] [{level}] [{module}] {text}"
    else:
        print(f"[{now}] [{level}] [{module}] {text}")
