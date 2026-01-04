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
    
    # Convenience functions
    'extract_with_ai',
]
