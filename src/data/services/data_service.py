"""Main data service for accessing all data sources."""
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..base import (
    DataSource, DataSourceRegistry, DataRequest, DataResponse,
    TimeSeries, DataPoint, DataFrequency,
    DataSourceError, DataNotFoundError, ConfigurationError
)
from ..providers import WorldBankProvider, FileProvider
from .cache_manager import CacheManager
from ...core.logger import get_logger

logger = get_logger(__name__)


class DataService:
    """Main data service for accessing all data sources.
    
    Provides unified interface to:
    - Multiple data providers (World Bank, IRENA, files, etc.)
    - Intelligent caching
    - Fallback mechanisms
    - Data validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize cache
        cache_config = self.config.get('cache', {})
        self.cache = CacheManager(cache_config)
        
        # Initialize providers
        self._initialize_providers()
        
        # Settings
        self.fallback_enabled = self.config.get('enable_fallback', True)
        self.prefer_cached = self.config.get('prefer_cached', True)
        
        logger.info(f"Data service initialized with {len(DataSourceRegistry.get_all())} providers")
    
    def _initialize_providers(self):
        """Initialize all data providers from config."""
        providers_config = self.config.get('providers', {})
        
        # World Bank
        if providers_config.get('world_bank', {}).get('enabled', True):
            wb_provider = WorldBankProvider(providers_config.get('world_bank', {}))
            DataSourceRegistry.register('world_bank', wb_provider)
            logger.info("Registered World Bank provider")
        
        # File provider
        if providers_config.get('file', {}).get('enabled', True):
            file_provider = FileProvider(providers_config.get('file', {}))
            DataSourceRegistry.register('file', file_provider)
            logger.info("Registered File provider")
        
        # Add more providers here as they're implemented
        # e.g., IRENA, IEA, Euromoney, etc.
    
    def get_data(
        self,
        country: str,
        indicator: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None,
        use_cache: bool = True
    ) -> DataResponse:
        """Get data for country and indicator.
        
        Args:
            country: Country name
            indicator: Indicator name
            start_date: Start date (optional)
            end_date: End date (optional)
            source: Specific source to use (optional)
            use_cache: Whether to use cache
            
        Returns:
            DataResponse with data
        """
        try:
            # Create request
            request = DataRequest(
                country=country,
                indicator=indicator,
                start_date=start_date,
                end_date=end_date,
                source=source,
                use_cache=use_cache
            )
            
            # Check cache first
            if use_cache and self.prefer_cached:
                cached = self.cache.get(country, indicator, source or "any")
                if cached:
                    logger.debug(f"Returning cached data for {country} - {indicator}")
                    return cached
            
            # Get provider(s)
            if source:
                # Use specific source
                provider = DataSourceRegistry.get(source)
                if not provider:
                    return DataResponse(
                        data=None,
                        success=False,
                        error=f"Provider '{source}' not found",
                        source=source or "unknown"
                    )
                
                response = self._fetch_from_provider(provider, request)
            else:
                # Try all providers for this indicator
                response = self._fetch_with_fallback(request)
            
            # Cache successful responses
            if response.success and use_cache:
                frequency = self._get_frequency(response.source, indicator)
                self.cache.set(response, frequency=frequency)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            return DataResponse(
                data=None,
                success=False,
                error=str(e),
                source=source or "unknown"
            )
    
    def get_latest(
        self,
        country: str,
        indicator: str,
        source: Optional[str] = None
    ) -> Optional[DataPoint]:
        """Get latest data point.
        
        Args:
            country: Country name
            indicator: Indicator name
            source: Specific source (optional)
            
        Returns:
            Latest DataPoint or None
        """
        response = self.get_data(country, indicator, source=source)
        
        if response.success and response.data:
            return response.data.get_latest()
        
        return None
    
    def get_value(
        self,
        country: str,
        indicator: str,
        default: Optional[float] = None,
        source: Optional[str] = None
    ) -> Optional[float]:
        """Get latest value for indicator.
        
        Args:
            country: Country name
            indicator: Indicator name
            default: Default value if not found
            source: Specific source (optional)
            
        Returns:
            Latest value or default
        """
        point = self.get_latest(country, indicator, source)
        
        if point:
            return point.value
        
        return default
    
    def _fetch_from_provider(
        self, 
        provider: DataSource, 
        request: DataRequest
    ) -> DataResponse:
        """Fetch data from specific provider."""
        if not provider.is_available():
            return DataResponse(
                data=None,
                success=False,
                error=f"Provider {provider.name} not available",
                source=provider.name
            )
        
        if not provider.validate_request(request):
            return DataResponse(
                data=None,
                success=False,
                error=f"Invalid request for provider {provider.name}",
                source=provider.name
            )
        
        return provider.fetch_data(request)
    
    def _fetch_with_fallback(self, request: DataRequest) -> DataResponse:
        """Fetch data with fallback to multiple providers."""
        # Get providers that support this indicator
        providers = DataSourceRegistry.get_for_indicator(request.indicator)
        
        if not providers:
            return DataResponse(
                data=None,
                success=False,
                error=f"No provider found for indicator: {request.indicator}",
                source="none"
            )
        
        # Try each provider
        errors = []
        for provider in providers:
            logger.debug(f"Trying provider: {provider.name}")
            
            response = self._fetch_from_provider(provider, request)
            
            if response.success:
                return response
            
            errors.append(f"{provider.name}: {response.error}")
            
            if not self.fallback_enabled:
                break
        
        # All providers failed
        return DataResponse(
            data=None,
            success=False,
            error=f"All providers failed: {'; '.join(errors)}",
            source="multiple"
        )
    
    def _get_frequency(self, source: str, indicator: str) -> DataFrequency:
        """Get data frequency for caching."""
        provider = DataSourceRegistry.get(source)
        if provider:
            return provider.get_data_frequency(indicator)
        return DataFrequency.MONTHLY
    
    def get_available_indicators(self) -> List[str]:
        """Get all available indicators across all providers."""
        indicators = set()
        for provider in DataSourceRegistry.get_all().values():
            if provider.is_available():
                indicators.update(provider.get_supported_indicators())
        return sorted(list(indicators))
    
    def get_available_countries(self) -> List[str]:
        """Get all available countries across all providers."""
        countries = set()
        for provider in DataSourceRegistry.get_all().values():
            if provider.is_available():
                countries.update(provider.get_supported_countries())
        return sorted(list(countries))
    
    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """Get information about a provider."""
        provider = DataSourceRegistry.get(provider_name)
        if provider:
            return provider.get_metadata()
        return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of data service."""
        providers_status = {}
        for name, provider in DataSourceRegistry.get_all().items():
            providers_status[name] = {
                'available': provider.is_available(),
                'indicators': len(provider.get_supported_indicators()),
                'countries': len(provider.get_supported_countries())
            }
        
        return {
            'providers': providers_status,
            'cache': self.cache.get_stats(),
            'total_indicators': len(self.get_available_indicators()),
            'total_countries': len(self.get_available_countries())
        }
