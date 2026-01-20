"""
Verifies the package is installed accessible.
"""

from sys import path
print("Python system path:")
print(path)

print("Importing full package")
import pub_oapi_tools_common

print("Importing a single module")
from pub_oapi_tools_common import ucpms_db

print("Importing a single function")
from pub_oapi_tools_common.misc import log

log("INFO", __name__, "Testing the imported function.")

print("Packages imported successfully. Exiting.")
