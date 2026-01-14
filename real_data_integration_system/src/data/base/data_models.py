"""Data models for the data integration system."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from .data_types import DataQuality, DataCategory


@dataclass
class DataPoint:
    """Single data point with metadata."""
    
    value: float
    timestamp: datetime
    country: str
    indicator: str
    source: str
    quality: DataQuality = DataQuality.UNKNOWN
    unit: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'country': self.country,
            'indicator': self.indicator,
            'source': self.source,
            'quality': self.quality.value,
            'unit': self.unit,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataPoint':
        """Create from dictionary."""
        return cls(
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            country=data['country'],
            indicator=data['indicator'],
            source=data['source'],
            quality=DataQuality(data.get('quality', 'unknown')),
            unit=data.get('unit'),
            metadata=data.get('metadata', {})
        )


@dataclass
class TimeSeries:
    """Time series of data points."""
    
    country: str
    indicator: str
    data_points: List[DataPoint] = field(default_factory=list)
    source: str = ""
    category: Optional[DataCategory] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_point(self, point: DataPoint):
        """Add data point."""
        self.data_points.append(point)
    
    def get_latest(self) -> Optional[DataPoint]:
        """Get most recent data point."""
        if not self.data_points:
            return None
        return max(self.data_points, key=lambda p: p.timestamp)
    
    def get_value_at(self, date: datetime) -> Optional[float]:
        """Get value at specific date."""
        for point in self.data_points:
            if point.timestamp == date:
                return point.value
        return None
    
    def get_average(self) -> Optional[float]:
        """Get average value."""
        if not self.data_points:
            return None
        return sum(p.value for p in self.data_points) / len(self.data_points)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'country': self.country,
            'indicator': self.indicator,
            'source': self.source,
            'category': self.category.value if self.category else None,
            'data_points': [p.to_dict() for p in self.data_points],
            'metadata': self.metadata
        }


@dataclass
class DataRequest:
    """Request for data."""
    
    country: str
    indicator: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = None
    use_cache: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataResponse:
    """Response from data source."""
    
    data: Optional[TimeSeries]
    success: bool
    error: Optional[str] = None
    source: str = ""
    cached: bool = False
    fetch_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
