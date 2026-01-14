"""
Exceptions for regulatory filing operations.
"""

class FilingError(Exception):
    """Base exception for filing operations."""
    pass


class FilingAPIError(FilingError):
    """Exception for API filing errors."""
    pass
