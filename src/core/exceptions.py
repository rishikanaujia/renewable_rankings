"""Custom exceptions for the application."""


class RankingSystemError(Exception):
    """Base exception for all ranking system errors."""
    pass


class ConfigurationError(RankingSystemError):
    """Raised when configuration is invalid or missing."""
    pass


class DataValidationError(RankingSystemError):
    """Raised when data validation fails."""
    pass


class ServiceError(RankingSystemError):
    """Raised when a service operation fails."""
    pass


class AgentError(RankingSystemError):
    """Raised when an agent operation fails."""
    pass


class MemoryError(RankingSystemError):
    """Raised when memory operation fails."""
    pass
