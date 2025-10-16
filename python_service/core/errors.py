# python_service/core/errors.py
from enum import Enum

class ErrorCategory(Enum):
    CONFIGURATION_ERROR = "Configuration missing or invalid"
    NETWORK_ERROR = "HTTP/Network request failed"
    PARSING_ERROR = "Data parsing or validation unsuccessful"
    UNEXPECTED_ERROR = "An unhandled exception occurred"