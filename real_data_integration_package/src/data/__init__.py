"""Data integration package.

Provides unified access to multiple data sources.
"""
from .base import (
    DataSourceType, DataCategory, DataFrequency, DataQuality,
    DataPoint, TimeSeries, DataRequest, DataResponse,
    DataSource, DataSourceRegistry,
    DataIntegrationError, DataSourceError, DataNotFoundError
)
from .providers import WorldBankProvider, FileProvider
from .services import DataService, CacheManager

__all__ = [
    'DataSourceType', 'DataCategory', 'DataFrequency', 'DataQuality',
    'DataPoint', 'TimeSeries', 'DataRequest', 'DataResponse',
    'DataSource', 'DataSourceRegistry',
    'WorldBankProvider', 'FileProvider',
    'DataService', 'CacheManager',
    'DataIntegrationError', 'DataSourceError', 'DataNotFoundError',
]

