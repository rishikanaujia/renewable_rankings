"""File-based data provider for CSV/Excel files."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import time

from src.core.logger import get_logger

from ..base import (
    DataSource, DataRequest, DataResponse, TimeSeries, DataPoint,
    DataSourceType, DataQuality, DataFrequency,
    DataSourceError, DataNotFoundError
)

logger = get_logger(__name__)


class FileProvider(DataSource):
    """File-based data provider.
    
    Supports CSV and Excel files for custom datasets.
    Useful for proprietary data, testing, and offline operation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize file provider.
        
        Args:
            config: Configuration dictionary with 'data_directory' key
        """
        super().__init__(config)
        
        self.data_directory = Path(config.get('data_directory', './data/files')) if config else Path('./data/files')
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # Lazy import pandas
        try:
            import pandas as pd
            self.pd = pd
        except ImportError:
            logger.warning("pandas not available - File provider disabled")
            self.enabled = False
            self.pd = None
        
        # Cache of loaded files
        self._file_cache: Dict[str, Any] = {}
        
        # Scan for available files
        self._scan_files()
    
    def _scan_files(self):
        """Scan data directory for available files."""
        self.available_files = {}
        
        if not self.data_directory.exists():
            return
        
        for file_path in self.data_directory.glob('*'):
            if file_path.suffix in ['.csv', '.xlsx', '.xls']:
                # Extract metadata from filename
                # Expected format: {indicator}_{country}.csv or {indicator}.csv
                name = file_path.stem
                parts = name.split('_')
                
                if len(parts) >= 2:
                    indicator = parts[0]
                    country = '_'.join(parts[1:])
                else:
                    indicator = name
                    country = 'global'
                
                key = f"{indicator}_{country}"
                self.available_files[key] = file_path
                
                logger.debug(f"Found file: {indicator} for {country} at {file_path}")
    
    def get_source_type(self) -> DataSourceType:
        """Get data source type."""
        return DataSourceType.FILE
    
    def get_supported_indicators(self) -> List[str]:
        """Get list of supported indicators."""
        indicators = set()
        for key in self.available_files.keys():
            indicator = key.split('_')[0]
            indicators.add(indicator)
        return list(indicators)
    
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries."""
        countries = set()
        for key in self.available_files.keys():
            parts = key.split('_')
            if len(parts) > 1:
                country = '_'.join(parts[1:])
                countries.add(country)
        return list(countries)
    
    def validate_request(self, request: DataRequest) -> bool:
        """Validate if request can be fulfilled."""
        key = f"{request.indicator}_{request.country}"
        return key in self.available_files
    
    def fetch_data(self, request: DataRequest) -> DataResponse:
        """Fetch data from file."""
        if not self.enabled:
            return DataResponse(
                data=None,
                success=False,
                error="File provider not available (pandas required)",
                source="file"
            )
        
        start_time = time.time()
        
        try:
            key = f"{request.indicator}_{request.country}"
            
            if key not in self.available_files:
                return DataResponse(
                    data=None,
                    success=False,
                    error=f"No file found for {request.indicator} - {request.country}",
                    source="file"
                )
            
            file_path = self.available_files[key]
            
            # Load file
            df = self._load_file(file_path)
            
            # Parse into time series
            time_series = self._parse_file(df, request, file_path)
            
            fetch_time = (time.time() - start_time) * 1000
            
            return DataResponse(
                data=time_series,
                success=True,
                source="file",
                fetch_time_ms=fetch_time,
                metadata={'file_path': str(file_path)}
            )
            
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            fetch_time = (time.time() - start_time) * 1000
            return DataResponse(
                data=None,
                success=False,
                error=str(e),
                source="file",
                fetch_time_ms=fetch_time
            )
    
    def _load_file(self, file_path: Path) -> Any:
        """Load file with caching."""
        # Check cache
        cache_key = str(file_path)
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]
        
        # Load based on extension
        if file_path.suffix == '.csv':
            df = self.pd.read_csv(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = self.pd.read_excel(file_path)
        else:
            raise DataSourceError(f"Unsupported file type: {file_path.suffix}")
        
        # Cache it
        self._file_cache[cache_key] = df
        
        return df
    
    def _parse_file(
        self, 
        df: Any, 
        request: DataRequest,
        file_path: Path
    ) -> TimeSeries:
        """Parse dataframe into time series.
        
        Expected columns: date, value
        Optional columns: quality, unit
        """
        time_series = TimeSeries(
            country=request.country,
            indicator=request.indicator,
            source="file"
        )
        
        # Validate required columns
        if 'date' not in df.columns or 'value' not in df.columns:
            raise DataSourceError("File must have 'date' and 'value' columns")
        
        for _, row in df.iterrows():
            try:
                # Parse date
                if isinstance(row['date'], str):
                    timestamp = datetime.fromisoformat(row['date'])
                elif isinstance(row['date'], int):
                    # Assume year
                    timestamp = datetime(row['date'], 12, 31)
                else:
                    timestamp = row['date']
                
                # Get quality
                quality_str = row.get('quality', 'unknown')
                try:
                    quality = DataQuality(quality_str)
                except ValueError:
                    quality = DataQuality.UNKNOWN
                
                # Create data point
                point = DataPoint(
                    value=float(row['value']),
                    timestamp=timestamp,
                    country=request.country,
                    indicator=request.indicator,
                    source="file",
                    quality=quality,
                    unit=row.get('unit'),
                    metadata={'file': str(file_path.name)}
                )
                
                time_series.add_point(point)
                
            except Exception as e:
                logger.warning(f"Skipping row: {e}")
                continue
        
        return time_series
    
    def get_data_frequency(self, indicator: str) -> DataFrequency:
        """Get update frequency for indicator."""
        # Files are static unless manually updated
        return DataFrequency.STATIC
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.enabled and self.pd is not None and len(self.available_files) > 0
