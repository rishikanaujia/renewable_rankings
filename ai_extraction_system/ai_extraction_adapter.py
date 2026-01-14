"""AI Extraction Adapter - Integration layer between AI extractors and existing agents.

This adapter provides a clean interface for existing parameter agents to use
AI-powered extraction without modifying their core logic.

Design Pattern:
    - Adapter Pattern: Adapts AI extraction system to existing agent interface
    - Strategy Pattern: Different extractors for different parameters
    - Factory Pattern: Creates appropriate extractor based on parameter

Usage in existing agents:
    ```python
    # In existing parameter agent _fetch_data() method:
    elif self.mode == AgentMode.AI_POWERED:
        from ai_extraction_adapter import AIExtractionAdapter
        
        adapter = AIExtractionAdapter(
            llm_config=self.config.get('llm_config'),
            cache_config=self.config.get('cache_config')
        )
        
        return adapter.extract_parameter(
            parameter_name=self.parameter_name,
            country=country,
            period=period,
            documents=self._get_documents(country)
        )
    ```

No modifications needed to existing agent code beyond adding this block!
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .base_extractor import BaseExtractor, ExtractionResult
from .llm_service import LLMService, LLMConfig, LLMProvider
from .cache.extraction_cache import ExtractionCache
from .processors.document_processor import DocumentProcessor, ProcessedDocument
from .extractors.ambition_extractor import AmbitionExtractor


logger = logging.getLogger(__name__)


class AIExtractionAdapter:
    """Adapter for integrating AI extraction with existing parameter agents.
    
    This class provides a simplified interface for existing agents to use
    AI-powered extraction without major code changes.
    
    Example:
        >>> adapter = AIExtractionAdapter()
        >>> result = adapter.extract_parameter(
        ...     parameter_name="ambition",
        ...     country="Germany",
        ...     period="Q3 2024",
        ...     documents=[...]
        ... )
        >>> print(result['value'])
    """
    
    def __init__(
        self,
        llm_config: Optional[Dict[str, Any]] = None,
        cache_config: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize AI extraction adapter.
        
        Args:
            llm_config: LLM configuration dictionary
            cache_config: Cache configuration dictionary  
            config: General configuration dictionary
        """
        self.config = config or {}
        
        # Initialize LLM service
        self.llm_service = self._initialize_llm_service(llm_config)
        
        # Initialize cache
        self.cache = self._initialize_cache(cache_config)
        
        # Initialize document processor
        self.document_processor = DocumentProcessor(
            config=self.config.get('document_processor', {})
        )
        
        # Registry of extractors (lazy initialization)
        self._extractors: Dict[str, BaseExtractor] = {}
        
        logger.info("Initialized AIExtractionAdapter")
    
    def extract_parameter(
        self,
        parameter_name: str,
        country: str,
        period: str,
        documents: Optional[List[Dict[str, Any]]] = None,
        document_urls: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Extract parameter value using AI.
        
        This is the main entry point for parameter extraction.
        
        Args:
            parameter_name: Name of parameter to extract (e.g., "ambition")
            country: Country name
            period: Time period (e.g., "Q3 2024")
            documents: Optional list of pre-processed documents
            document_urls: Optional list of URLs to fetch and process
            use_cache: Whether to use caching
            
        Returns:
            Dictionary compatible with existing agent data format:
            {
                'value': <extracted value>,
                'confidence': <0.0-1.0>,
                'source': 'ai_powered',
                'justification': <explanation>,
                'metadata': {...},
                'period': <period>
            }
        """
        try:
            logger.info(
                f"Extracting {parameter_name} for {country} ({period}) "
                f"using AI-powered extraction"
            )
            
            # Get or create extractor for this parameter
            extractor = self._get_extractor(parameter_name)
            
            # Process documents if needed
            processed_docs = self._prepare_documents(
                documents=documents,
                document_urls=document_urls,
                parameter_name=parameter_name,
                country=country
            )
            
            if not processed_docs:
                logger.warning(f"No documents available for {parameter_name} - {country}")
                return self._create_fallback_result(
                    parameter_name,
                    "No documents available for extraction"
                )
            
            # Perform extraction
            result = extractor.extract(
                country=country,
                documents=processed_docs,
                context={'period': period}
            )
            
            # Convert to agent-compatible format
            return self._convert_extraction_result(result, period)
        
        except Exception as e:
            logger.error(
                f"AI extraction failed for {parameter_name} - {country}: {e}",
                exc_info=True
            )
            return self._create_fallback_result(
                parameter_name,
                f"Extraction error: {str(e)}"
            )
    
    def _get_extractor(self, parameter_name: str) -> BaseExtractor:
        """Get or create extractor for parameter.
        
        Args:
            parameter_name: Parameter name
            
        Returns:
            BaseExtractor instance
        """
        # Return cached extractor if exists
        if parameter_name in self._extractors:
            return self._extractors[parameter_name]
        
        # Create new extractor
        extractor = self._create_extractor(parameter_name)
        
        # Cache for reuse
        self._extractors[parameter_name] = extractor
        
        return extractor
    
    def _create_extractor(self, parameter_name: str) -> BaseExtractor:
        """Factory method to create appropriate extractor.
        
        Args:
            parameter_name: Parameter name
            
        Returns:
            BaseExtractor instance for the parameter
        """
        from .extractors.generic_extractor import create_generic_extractor
        from .config.parameter_configs import PARAMETER_CONFIGS
        
        # Specialized extractors for complex parameters
        specialized_extractors = {
            'ambition': AmbitionExtractor,
            # Add more specialized extractors here if needed
        }
        
        # Check if specialized extractor exists
        if parameter_name in specialized_extractors:
            extractor_class = specialized_extractors[parameter_name]
            return extractor_class(
                parameter_name=parameter_name,
                llm_service=self.llm_service,
                cache=self.cache,
                config=self.config
            )
        
        # Use generic extractor for all other parameters
        if parameter_name in PARAMETER_CONFIGS:
            return create_generic_extractor(
                parameter_name=parameter_name,
                llm_service=self.llm_service,
                cache=self.cache,
                config=self.config
            )
        
        # Parameter not configured
        raise NotImplementedError(
            f"AI extractor not configured for parameter: {parameter_name}. "
            f"Add configuration to parameter_configs.py"
        )
    
    def _prepare_documents(
        self,
        documents: Optional[List[Dict[str, Any]]],
        document_urls: Optional[List[str]],
        parameter_name: str,
        country: str
    ) -> List[Dict[str, Any]]:
        """Prepare documents for extraction.
        
        Args:
            documents: Pre-processed documents
            document_urls: URLs to fetch
            parameter_name: Parameter being extracted
            country: Country name
            
        Returns:
            List of document dictionaries with 'content' and 'metadata'
        """
        prepared_docs = []
        
        # Use provided documents if available
        if documents:
            prepared_docs.extend(documents)
        
        # Fetch and process URLs if provided
        if document_urls:
            for url in document_urls:
                try:
                    processed = self.document_processor.process_url(url)
                    prepared_docs.append({
                        'content': processed.content,
                        'metadata': processed.metadata
                    })
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
        
        # If no documents provided, try to fetch recommended sources
        if not prepared_docs:
            logger.info(
                f"No documents provided, attempting to fetch recommended sources "
                f"for {parameter_name} - {country}"
            )
            prepared_docs = self._fetch_recommended_documents(parameter_name, country)
        
        return prepared_docs
    
    def _fetch_recommended_documents(
        self,
        parameter_name: str,
        country: str
    ) -> List[Dict[str, Any]]:
        """Fetch documents from recommended sources.
        
        Args:
            parameter_name: Parameter name
            country: Country name
            
        Returns:
            List of processed documents
        """
        # This would be implemented to automatically fetch from known sources
        # For now, return empty list
        logger.info(
            f"Automatic document fetching not yet implemented for {parameter_name}"
        )
        return []
    
    def _convert_extraction_result(
        self,
        result: ExtractionResult,
        period: str
    ) -> Dict[str, Any]:
        """Convert ExtractionResult to agent-compatible format.
        
        Args:
            result: ExtractionResult from extractor
            period: Time period
            
        Returns:
            Dictionary compatible with existing agent data format
        """
        if not result.success or not result.data:
            return self._create_fallback_result(
                "unknown",
                result.error or "Extraction failed"
            )
        
        data = result.data
        
        return {
            'value': data.value,
            'confidence': data.confidence,
            'source': 'ai_powered',
            'justification': data.justification,
            'quotes': data.extracted_quotes,
            'sources': data.sources,
            'metadata': {
                **data.metadata,
                'extraction_timestamp': data.extraction_timestamp.isoformat(),
                'confidence_level': data.confidence_level.value,
                'cached': result.cached,
                'extraction_duration_ms': result.extraction_duration_ms
            },
            'period': period
        }
    
    def _create_fallback_result(
        self,
        parameter_name: str,
        error_message: str
    ) -> Dict[str, Any]:
        """Create fallback result when extraction fails.
        
        Args:
            parameter_name: Parameter name
            error_message: Error description
            
        Returns:
            Fallback data dictionary
        """
        return {
            'value': None,
            'confidence': 0.0,
            'source': 'ai_powered_failed',
            'justification': f"AI extraction failed: {error_message}",
            'quotes': [],
            'sources': [],
            'metadata': {
                'error': error_message,
                'parameter': parameter_name
            },
            'period': 'unknown'
        }
    
    def _initialize_llm_service(
        self,
        llm_config: Optional[Dict[str, Any]]
    ) -> LLMService:
        """Initialize LLM service from configuration.
        
        Args:
            llm_config: LLM configuration dictionary
            
        Returns:
            Initialized LLMService
        """
        if llm_config:
            config = LLMConfig(**llm_config)
        else:
            # Default configuration (Claude Sonnet)
            config = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                temperature=0.1,
                max_tokens=2000
            )
        
        return LLMService(config)
    
    def _initialize_cache(
        self,
        cache_config: Optional[Dict[str, Any]]
    ) -> Optional[ExtractionCache]:
        """Initialize extraction cache.
        
        Args:
            cache_config: Cache configuration dictionary
            
        Returns:
            ExtractionCache instance or None
        """
        if cache_config is None or cache_config.get('enabled', True):
            cache_dir = cache_config.get('cache_dir') if cache_config else None
            if cache_dir:
                cache_dir = Path(cache_dir)
            
            ttl = cache_config.get('ttl', 86400) if cache_config else 86400
            
            return ExtractionCache(
                cache_dir=cache_dir,
                default_ttl=ttl
            )
        
        return None
    
    def get_supported_parameters(self) -> List[str]:
        """Get list of parameters with AI extractors implemented.
        
        Returns:
            List of parameter names
        """
        from .config.parameter_configs import list_parameters
        return list_parameters()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'llm_stats': self.llm_service.get_stats().__dict__,
            'supported_parameters': self.get_supported_parameters(),
            'extractors_cached': len(self._extractors)
        }
        
        if self.cache:
            stats['cache_stats'] = self.cache.get_stats()
        
        return stats


# Convenience function for quick integration
def extract_with_ai(
    parameter_name: str,
    country: str,
    period: str = "Q3 2024",
    documents: Optional[List[Dict[str, Any]]] = None,
    **config
) -> Dict[str, Any]:
    """Quick extraction function for existing agents.
    
    Args:
        parameter_name: Parameter to extract
        country: Country name
        period: Time period
        documents: Optional documents to analyze
        **config: Configuration options
        
    Returns:
        Extracted data dictionary
    """
    adapter = AIExtractionAdapter(
        llm_config=config.get('llm_config'),
        cache_config=config.get('cache_config'),
        config=config
    )
    
    return adapter.extract_parameter(
        parameter_name=parameter_name,
        country=country,
        period=period,
        documents=documents
    )
