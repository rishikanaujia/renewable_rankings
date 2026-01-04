"""World Bank API data provider.

Official API documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from src.core.logger import get_logger

from ..base import (
    DataSource, DataRequest, DataResponse, TimeSeries, DataPoint,
    DataSourceType, DataQuality, DataFrequency,
    DataSourceError, DataNotFoundError, RateLimitError,
    COUNTRY_CODES, WORLD_BANK_INDICATORS
)

logger = get_logger(__name__)


class WorldBankProvider(DataSource):
    """World Bank API data provider.
    
    Provides access to World Bank's extensive economic and development indicators.
    Free API, no authentication required.
    """
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize World Bank provider.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        self.timeout = config.get('timeout', 30) if config else 30
        self.retries = config.get('retries', 3) if config else 3
        self.retry_delay = config.get('retry_delay', 2) if config else 2
        
        # Lazy import requests
        try:
            import requests
            self.requests = requests
        except ImportError:
            logger.warning("requests library not available - World Bank provider disabled")
            self.enabled = False
            self.requests = None
    
    def get_source_type(self) -> DataSourceType:
        """Get data source type."""
        return DataSourceType.API
    
    def get_supported_indicators(self) -> List[str]:
        """Get list of supported indicators."""
        return list(WORLD_BANK_INDICATORS.keys())
    
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries."""
        return list(COUNTRY_CODES.keys())
    
    def validate_request(self, request: DataRequest) -> bool:
        """Validate if request can be fulfilled."""
        if request.indicator not in WORLD_BANK_INDICATORS:
            return False
        if request.country not in COUNTRY_CODES:
            return False
        return True
    
    def fetch_data(self, request: DataRequest) -> DataResponse:
        """Fetch data from World Bank API."""
        if not self.enabled:
            return DataResponse(
                data=None,
                success=False,
                error="World Bank provider not available",
                source="world_bank"
            )
        
        start_time = time.time()
        
        try:
            # Validate request
            if not self.validate_request(request):
                return DataResponse(
                    data=None,
                    success=False,
                    error=f"Invalid request: {request.indicator} for {request.country}",
                    source="world_bank"
                )
            
            # Get indicator code and country code
            indicator_code = WORLD_BANK_INDICATORS[request.indicator]
            country_code = COUNTRY_CODES[request.country]
            
            # Fetch data with retries
            data = self._fetch_with_retry(country_code, indicator_code, request)
            
            if not data:
                return DataResponse(
                    data=None,
                    success=False,
                    error="No data returned from API",
                    source="world_bank"
                )
            
            # Parse response
            time_series = self._parse_response(data, request)
            
            fetch_time = (time.time() - start_time) * 1000
            
            return DataResponse(
                data=time_series,
                success=True,
                source="world_bank",
                fetch_time_ms=fetch_time,
                metadata={
                    'indicator_code': indicator_code,
                    'country_code': country_code
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching from World Bank: {e}")
            fetch_time = (time.time() - start_time) * 1000
            return DataResponse(
                data=None,
                success=False,
                error=str(e),
                source="world_bank",
                fetch_time_ms=fetch_time
            )
    
    def _fetch_with_retry(
        self, 
        country_code: str, 
        indicator_code: str,
        request: DataRequest
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch data with retry logic."""
        # Build URL
        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        
        # Build parameters
        params = {
            'format': 'json',
            'per_page': 100
        }
        
        if request.start_date:
            params['date'] = f"{request.start_date.year}:{request.end_date.year if request.end_date else datetime.now().year}"
        
        # Retry logic
        last_error = None
        for attempt in range(self.retries):
            try:
                logger.debug(f"Fetching from World Bank (attempt {attempt + 1}): {url}")
                
                response = self.requests.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    # Rate limit
                    logger.warning("Rate limit hit, waiting...")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
                response.raise_for_status()
                
                # Parse JSON
                json_data = response.json()
                
                # World Bank returns array: [metadata, data]
                if isinstance(json_data, list) and len(json_data) > 1:
                    return json_data[1]  # Return data part
                
                return None
                
            except self.requests.exceptions.Timeout:
                last_error = "Request timeout"
                logger.warning(f"Timeout on attempt {attempt + 1}")
                time.sleep(self.retry_delay)
                
            except self.requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                time.sleep(self.retry_delay)
        
        # All retries failed
        raise DataSourceError(f"Failed after {self.retries} attempts: {last_error}")
    
    def _parse_response(
        self, 
        data: List[Dict[str, Any]], 
        request: DataRequest
    ) -> TimeSeries:
        """Parse World Bank API response."""
        time_series = TimeSeries(
            country=request.country,
            indicator=request.indicator,
            source="world_bank"
        )
        
        for item in data:
            if item.get('value') is None:
                continue
            
            try:
                # Parse date
                date_str = item.get('date', '')
                year = int(date_str)
                timestamp = datetime(year, 12, 31)  # Use end of year
                
                # Create data point
                point = DataPoint(
                    value=float(item['value']),
                    timestamp=timestamp,
                    country=request.country,
                    indicator=request.indicator,
                    source="world_bank",
                    quality=DataQuality.OFFICIAL,
                    unit=item.get('unit', ''),
                    metadata={
                        'country_id': item.get('country', {}).get('id'),
                        'country_name': item.get('country', {}).get('value'),
                        'indicator_id': item.get('indicator', {}).get('id'),
                        'indicator_name': item.get('indicator', {}).get('value'),
                    }
                )
                
                time_series.add_point(point)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid data point: {e}")
                continue
        
        return time_series
    
    def get_data_frequency(self, indicator: str) -> DataFrequency:
        """Get update frequency for indicator."""
        # World Bank data is typically annual
        return DataFrequency.ANNUAL
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        if not self.enabled or not self.requests:
            return False
        
        try:
            # Quick health check
            response = self.requests.get(
                f"{self.BASE_URL}/country/USA/indicator/NY.GDP.MKTP.CD",
                params={'format': 'json', 'per_page': 1},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
