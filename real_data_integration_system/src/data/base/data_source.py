"""Abstract base class for data sources."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from .data_models import DataRequest, DataResponse, TimeSeries, DataPoint
from .data_types import DataSourceType, DataCategory, DataFrequency
from .exceptions import DataSourceError


class DataSource(ABC):
    """Abstract base class for all data sources.
    
    All data providers must implement this interface.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data source.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self.enabled = self.config.get('enabled', True)
    
    @abstractmethod
    def get_source_type(self) -> DataSourceType:
        """Get data source type."""
        pass
    
    @abstractmethod
    def get_supported_indicators(self) -> List[str]:
        """Get list of supported indicators."""
        pass
    
    @abstractmethod
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries."""
        pass
    
    @abstractmethod
    def fetch_data(self, request: DataRequest) -> DataResponse:
        """Fetch data from source.
        
        Args:
            request: Data request
            
        Returns:
            Data response
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: DataRequest) -> bool:
        """Validate if request can be fulfilled.
        
        Args:
            request: Data request
            
        Returns:
            True if valid
        """
        pass
    
    def get_data_frequency(self, indicator: str) -> DataFrequency:
        """Get update frequency for indicator.
        
        Args:
            indicator: Indicator name
            
        Returns:
            Data frequency
        """
        return DataFrequency.MONTHLY  # Default
    
    def is_available(self) -> bool:
        """Check if data source is available.
        
        Returns:
            True if available
        """
        return self.enabled
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about this data source.
        
        Returns:
            Metadata dictionary
        """
        return {
            'name': self.name,
            'type': self.get_source_type().value,
            'enabled': self.enabled,
            'supported_indicators': len(self.get_supported_indicators()),
            'supported_countries': len(self.get_supported_countries()),
        }


class DataSourceRegistry:
    """Registry for data source providers."""
    
    _providers: Dict[str, DataSource] = {}
    
    @classmethod
    def register(cls, name: str, provider: DataSource):
        """Register a data provider.
        
        Args:
            name: Provider name
            provider: Provider instance
        """
        cls._providers[name] = provider
    
    @classmethod
    def get(cls, name: str) -> Optional[DataSource]:
        """Get provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None
        """
        return cls._providers.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, DataSource]:
        """Get all registered providers.
        
        Returns:
            Dictionary of providers
        """
        return cls._providers.copy()
    
    @classmethod
    def get_for_indicator(cls, indicator: str) -> List[DataSource]:
        """Get providers that support an indicator.
        
        Args:
            indicator: Indicator name
            
        Returns:
            List of providers
        """
        return [
            p for p in cls._providers.values()
            if indicator in p.get_supported_indicators() and p.is_available()
        ]
    
    @classmethod
    def clear(cls):
        """Clear all providers."""
        cls._providers.clear()
