"""Data source types and enums for the data integration system."""
from enum import Enum
from typing import List


class DataSourceType(str, Enum):
    """Types of data sources."""
    API = "api"                 # REST API
    DATABASE = "database"       # SQL database
    FILE = "file"              # CSV, Excel, JSON files
    WEBSCRAPE = "webscrape"    # Web scraping
    MANUAL = "manual"          # Manually entered data
    AGGREGATED = "aggregated"  # Combines multiple sources


class DataCategory(str, Enum):
    """Categories of data available."""
    ECONOMIC = "economic"                    # GDP, growth rates, etc.
    POLITICAL = "political"                  # Stability ratings, governance
    ENERGY = "energy"                        # Energy production, consumption
    RENEWABLE = "renewable"                  # Renewable energy specific
    FINANCIAL = "financial"                  # Interest rates, exchange rates
    INFRASTRUCTURE = "infrastructure"        # Grid, transmission
    REGULATORY = "regulatory"                # Policies, regulations
    MARKET = "market"                       # Market size, competition


class DataFrequency(str, Enum):
    """Data update frequency."""
    REALTIME = "realtime"      # Real-time updates
    DAILY = "daily"           # Daily updates
    WEEKLY = "weekly"         # Weekly updates
    MONTHLY = "monthly"       # Monthly updates
    QUARTERLY = "quarterly"   # Quarterly updates
    ANNUAL = "annual"         # Annual updates
    STATIC = "static"         # Rarely changes


class DataFormat(str, Enum):
    """Data format types."""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    EXCEL = "excel"
    PARQUET = "parquet"
    SQL = "sql"


class DataQuality(str, Enum):
    """Data quality levels."""
    VERIFIED = "verified"      # Verified by multiple sources
    OFFICIAL = "official"      # Official government/org data
    ESTIMATED = "estimated"    # Estimated/modeled data
    PRELIMINARY = "preliminary" # Preliminary/unverified
    UNKNOWN = "unknown"        # Quality unknown


class CacheStrategy(str, Enum):
    """Caching strategies."""
    NONE = "none"              # No caching
    MEMORY = "memory"          # In-memory cache
    DISK = "disk"             # Disk-based cache
    REDIS = "redis"           # Redis cache
    HYBRID = "hybrid"         # Memory + Disk


# Data field mappings for common indicators
ECONOMIC_INDICATORS = {
    'gdp': 'NY.GDP.MKTP.CD',              # GDP (current US$)
    'gdp_growth': 'NY.GDP.MKTP.KD.ZG',    # GDP growth (annual %)
    'gdp_per_capita': 'NY.GDP.PCAP.CD',   # GDP per capita
    'inflation': 'FP.CPI.TOTL.ZG',         # Inflation, consumer prices
    'unemployment': 'SL.UEM.TOTL.ZS',      # Unemployment rate
    'population': 'SP.POP.TOTL',           # Population, total
    'fdi': 'BX.KLT.DINV.WD.GD.ZS',        # FDI, net inflows (% of GDP)
}

ENERGY_INDICATORS = {
    'energy_use': 'EG.USE.PCAP.KG.OE',             # Energy use per capita
    'electricity_production': 'EG.ELC.PROD.KH',     # Electricity production
    'renewable_capacity': 'EG.ELC.RNWX.KH',        # Renewable capacity
    'renewable_consumption': 'EG.FEC.RNEW.ZS',     # Renewable energy consumption
    'co2_emissions': 'EN.ATM.CO2E.PC',             # CO2 emissions per capita
    'access_to_electricity': 'EG.ELC.ACCS.ZS',     # Access to electricity (%)
}

FINANCIAL_INDICATORS = {
    'interest_rate': 'FR.INR.RINR',                # Real interest rate
    'lending_rate': 'FR.INR.LEND',                 # Lending interest rate
    'exchange_rate': 'PA.NUS.FCRF',                # Exchange rate
    'inflation_gdp_deflator': 'NY.GDP.DEFL.KD.ZG', # Inflation, GDP deflator
}

# Country code mappings (ISO 3166-1 alpha-3)
COUNTRY_CODES = {
    'United States': 'USA',
    'Germany': 'DEU',
    'China': 'CHN',
    'India': 'IND',
    'Brazil': 'BRA',
    'United Kingdom': 'GBR',
    'Spain': 'ESP',
    'Australia': 'AUS',
    'Chile': 'CHL',
    'Vietnam': 'VNM',
    'South Africa': 'ZAF',
    'Nigeria': 'NGA',
    'Argentina': 'ARG',
    'Japan': 'JPN',
    'France': 'FRA',
    'Italy': 'ITA',
    'Canada': 'CAN',
    'Mexico': 'MEX',
    'Indonesia': 'IDN',
    'Turkey': 'TUR',
    'Saudi Arabia': 'SAU',
    'UAE': 'ARE',
    'Egypt': 'EGY',
    'Morocco': 'MAR',
    'Kenya': 'KEN',
    'Poland': 'POL',
    'Netherlands': 'NLD',
    'Belgium': 'BEL',
    'Sweden': 'SWE',
    'Norway': 'NOR',
    'Denmark': 'DNK',
    'Finland': 'FIN',
}

# Reverse mapping
CODE_TO_COUNTRY = {v: k for k, v in COUNTRY_CODES.items()}

# World Bank indicators - combined mapping for convenience
WORLD_BANK_INDICATORS = {
    **ECONOMIC_INDICATORS,
    **ENERGY_INDICATORS,
    **FINANCIAL_INDICATORS
}

# Default cache TTL by data frequency
CACHE_TTL_SECONDS = {
    DataFrequency.REALTIME: 60,          # 1 minute
    DataFrequency.DAILY: 86400,          # 1 day
    DataFrequency.WEEKLY: 604800,        # 7 days
    DataFrequency.MONTHLY: 2592000,      # 30 days
    DataFrequency.QUARTERLY: 7776000,    # 90 days
    DataFrequency.ANNUAL: 31536000,      # 365 days
    DataFrequency.STATIC: 157680000,     # 5 years
}

# Default configuration values
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 2
DEFAULT_CACHE_SIZE_MB = 100
