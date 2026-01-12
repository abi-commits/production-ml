"""
Custom exceptions for the application.
"""


class HousingMLError(Exception):
    """Base exception for Housing ML application."""

    pass


class ModelNotFoundError(HousingMLError):
    """Raised when model file is not found."""

    pass


class InvalidInputError(HousingMLError):
    """Raised when input data is invalid."""

    pass


class PredictionError(HousingMLError):
    """Raised when prediction fails."""

    pass


class ConfigurationError(HousingMLError):
    """Raised when configuration is invalid."""

    pass
