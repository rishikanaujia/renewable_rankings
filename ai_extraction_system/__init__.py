"""AI-Powered Parameter Extraction System

A production-ready framework for extracting renewable energy investment parameters
from documents using Large Language Models and LangChain.

Example Usage:
    >>> from ai_extraction_adapter import AIExtractionAdapter
    >>> 
    >>> adapter = AIExtractionAdapter()
    >>> result = adapter.extract_parameter(
    ...     parameter_name='ambition',
    ...     country='Germany',
    ...     period='Q3 2024'
    ... )
    >>> print(result['value'])

Main Components:
    - BaseExtractor: Abstract base class for all extractors
    - LLMService: LangChain wrapper for multi-provider LLM support
    - AIExtractionAdapter: Integration adapter for existing agents
    - DocumentProcessor: PDF/HTML/web document processing
    - ExtractionCache: Caching system for cost optimization

Author: AI Systems Team
Version: 1.0.0
"""

__version__ = '1.0.0'
__author__ = 'AI Systems Team'

# Core imports
from .base_extractor import BaseExtractor, ExtractedData, ExtractionResult
from .llm_service import LLMService, LLMConfig, LLMProvider
from .ai_extraction_adapter import AIExtractionAdapter, extract_with_ai

# Cache
from .cache.extraction_cache import ExtractionCache

# Processors
from .processors.document_processor import DocumentProcessor

# Extractors
from .extractors.ambition_extractor import AmbitionExtractor
from .extractors.competitive_landscape_extractor import CompetitiveLandscapeExtractor
from .extractors.contract_terms_extractor import ContractTermsExtractor
from .extractors.country_stability_extractor import CountryStabilityExtractor
from .extractors.energy_dependence_extractor import EnergyDependenceExtractor
from .extractors.expected_return_extractor import ExpectedReturnExtractor
from .extractors.support_scheme_extractor import SupportSchemeExtractor
from .extractors.track_record_extractor import TrackRecordExtractor
from .extractors.offtaker_status_extractor import OfftakerStatusExtractor
from .extractors.long_term_interest_rates_extractor import LongTermInterestRatesExtractor
from .extractors.power_market_size_extractor import PowerMarketSizeExtractor
from .extractors.renewables_penetration_extractor import RenewablesPenetrationExtractor
from .extractors.resource_availability_extractor import ResourceAvailabilityExtractor
from .extractors.revenue_stream_stability_extractor import RevenueStreamStabilityExtractor
from .extractors.status_of_grid_extractor import StatusOfGridExtractor
from .extractors.ownership_consolidation_extractor import OwnershipConsolidationExtractor
from .extractors.ownership_hurdles_extractor import OwnershipHurdlesExtractor
from .extractors.system_modifiers_extractor import SystemModifiersExtractor

__all__ = [
    # Core classes
    'BaseExtractor',
    'ExtractedData',
    'ExtractionResult',
    'LLMService',
    'LLMConfig',
    'LLMProvider',
    'AIExtractionAdapter',
    
    # Utilities
    'ExtractionCache',
    'DocumentProcessor',
    
    # Extractors
    'AmbitionExtractor',
    'CompetitiveLandscapeExtractor',
    'ContractTermsExtractor',
    'CountryStabilityExtractor',
    'EnergyDependenceExtractor',
    'ExpectedReturnExtractor',
    'SupportSchemeExtractor',
    'TrackRecordExtractor',
    'OfftakerStatusExtractor',
    'LongTermInterestRatesExtractor',
    'PowerMarketSizeExtractor',
    'RenewablesPenetrationExtractor',
    'ResourceAvailabilityExtractor',
    'RevenueStreamStabilityExtractor',
    'StatusOfGridExtractor',
    'OwnershipConsolidationExtractor',
    'OwnershipHurdlesExtractor',
    'SystemModifiersExtractor',

    # Convenience functions
    'extract_with_ai',
]
