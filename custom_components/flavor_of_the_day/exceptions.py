"""Custom exceptions for the Flavor of the Day integration."""

from __future__ import annotations


class FlavorProviderError(Exception):
    """Base exception for provider errors."""


class FlavorProviderCommunicationError(FlavorProviderError):
    """Exception to indicate a communication error with the provider."""


class FlavorProviderAuthenticationError(FlavorProviderError):
    """Exception to indicate an authentication error with the provider."""


class FlavorProviderTimeoutError(FlavorProviderCommunicationError):
    """Exception to indicate a timeout error with the provider."""


class LocationNotFoundError(FlavorProviderError):
    """Location ID not found."""


class FlavorNotAvailableError(FlavorProviderError):
    """Flavor data not available (store closed, no posting, etc.)."""


class RateLimitError(FlavorProviderCommunicationError):
    """Rate limit exceeded."""


class NetworkError(FlavorProviderCommunicationError):
    """Network connectivity issue."""


class FlavorProviderConfigError(FlavorProviderError):
    """Exception raised for provider configuration errors."""
