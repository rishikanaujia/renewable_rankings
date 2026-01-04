"""Custom exceptions for data integration system."""


class DataIntegrationError(Exception):
    """Base exception for data integration errors."""
    pass


class DataSourceError(DataIntegrationError):
    """Error from data source."""
    pass


class DataNotFoundError(DataIntegrationError):
    """Requested data not found."""
    pass


class DataValidationError(DataIntegrationError):
    """Data validation failed."""
    pass


class CacheError(DataIntegrationError):
    """Cache operation failed."""
    pass


class ConfigurationError(DataIntegrationError):
    """Configuration error."""
    pass


class RateLimitError(DataSourceError):
    """API rate limit exceeded."""
    pass


class AuthenticationError(DataSourceError):
    """Authentication failed."""
    pass
