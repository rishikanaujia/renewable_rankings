"""Base Extractor - Abstract base class for all AI-powered parameter extractors.

This module provides the foundation for AI-powered data extraction from documents.
All parameter-specific extractors inherit from this base class.

Architecture:
    BaseExtractor (abstract)
        ├── RegulationExtractor
        ├── ProfitabilityExtractor
        ├── MarketExtractor
        └── ... (one per subcategory or parameter)

Key Features:
    - LLM-based document analysis
    - Structured data extraction
    - Validation and confidence scoring
    - Source attribution
    - Caching support
    - Retry logic with exponential backoff

Design Principles:
    - Open/Closed: Open for extension, closed for modification
    - Single Responsibility: Each extractor handles one parameter type
    - Dependency Injection: LLM service, cache, and validators injected
    - Configuration-driven: All prompts and settings externalized
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json
import logging

from pydantic import BaseModel, Field, validator


logger = logging.getLogger(__name__)


class ExtractionConfidence(str, Enum):
    """Confidence levels for extracted data."""
    HIGH = "high"        # 0.8-1.0: Direct quotes, explicit statements
    MEDIUM = "medium"    # 0.5-0.8: Inferred from context
    LOW = "low"          # 0.0-0.5: Weak evidence, assumptions


class DocumentType(str, Enum):
    """Supported document types for extraction."""
    PDF = "pdf"
    HTML = "html"
    TEXT = "text"
    JSON = "json"


class ExtractedData(BaseModel):
    """Structured extracted data from documents."""
    
    parameter_name: str = Field(..., description="Name of the parameter extracted")
    value: Any = Field(..., description="Extracted parameter value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    confidence_level: ExtractionConfidence = Field(..., description="Confidence category")
    justification: str = Field(..., description="Explanation of how value was derived")
    sources: List[Dict[str, str]] = Field(default_factory=list, description="Source documents")
    extracted_quotes: List[str] = Field(default_factory=list, description="Relevant quotes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExtractionResult(BaseModel):
    """Complete extraction result with status and errors."""
    
    success: bool = Field(..., description="Whether extraction succeeded")
    data: Optional[ExtractedData] = Field(None, description="Extracted data if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    cached: bool = Field(default=False, description="Whether result came from cache")
    extraction_duration_ms: float = Field(default=0.0, description="Time taken in milliseconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseExtractor(ABC):
    """Abstract base class for all AI-powered parameter extractors.
    
    This class defines the interface and common functionality for extracting
    parameter data from documents using LLMs.
    
    Subclasses must implement:
        - _get_extraction_prompt(): Returns the LLM prompt template
        - _parse_llm_response(): Parses LLM output into structured data
        - _validate_extracted_data(): Validates extracted values
    
    Attributes:
        parameter_name: Name of the parameter this extractor handles
        llm_service: LLM service for document analysis
        cache: Optional cache for storing extraction results
        config: Configuration dictionary
    """
    
    def __init__(
        self,
        parameter_name: str,
        llm_service: 'LLMService',
        cache: Optional['ExtractionCache'] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the extractor.
        
        Args:
            parameter_name: Name of the parameter to extract
            llm_service: LLM service instance
            cache: Optional cache for results
            config: Optional configuration dictionary
        """
        self.parameter_name = parameter_name
        self.llm_service = llm_service
        self.cache = cache
        self.config = config or {}
        
        # Configuration defaults
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        self.use_cache = self.config.get('use_cache', True)
        self.cache_ttl = self.config.get('cache_ttl', 86400)  # 24 hours
        
        logger.info(f"Initialized {self.__class__.__name__} for parameter: {parameter_name}")
    
    @abstractmethod
    def _get_extraction_prompt(
        self,
        country: str,
        document_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the LLM prompt for extraction.
        
        Args:
            country: Country name
            document_content: Content to analyze
            context: Optional additional context
            
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def _parse_llm_response(
        self,
        llm_response: str,
        country: str
    ) -> Dict[str, Any]:
        """Parse LLM response into structured data.
        
        Args:
            llm_response: Raw LLM output
            country: Country name for context
            
        Returns:
            Dictionary with parsed data
        """
        pass
    
    @abstractmethod
    def _validate_extracted_data(
        self,
        data: Dict[str, Any],
        country: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate extracted data.
        
        Args:
            data: Extracted data dictionary
            country: Country name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    def extract(
        self,
        country: str,
        documents: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """Extract parameter value from documents.
        
        This is the main entry point for extraction. It handles:
        - Cache checking
        - Document processing
        - LLM invocation
        - Response parsing
        - Validation
        - Error handling
        
        Args:
            country: Country name
            documents: List of document dictionaries with 'content' and 'metadata'
            context: Optional additional context
            
        Returns:
            ExtractionResult with extracted data or error
        """
        start_time = datetime.now()
        
        try:
            logger.info(
                f"Starting extraction for {self.parameter_name} in {country} "
                f"with {len(documents)} documents"
            )
            
            # Check cache first
            if self.use_cache and self.cache:
                cached_result = self._check_cache(country, documents)
                if cached_result:
                    logger.info(f"Cache hit for {self.parameter_name} - {country}")
                    return cached_result
            
            # Prepare document content
            combined_content = self._prepare_documents(documents)
            
            # Generate prompt
            prompt = self._get_extraction_prompt(country, combined_content, context)
            
            # Invoke LLM with retry logic
            llm_response = self._invoke_llm_with_retry(prompt)
            
            # Parse response
            parsed_data = self._parse_llm_response(llm_response, country)
            
            # Validate data
            is_valid, error_msg = self._validate_extracted_data(parsed_data, country)
            if not is_valid:
                logger.warning(f"Validation failed for {country}: {error_msg}")
                return ExtractionResult(
                    success=False,
                    error=f"Validation error: {error_msg}",
                    extraction_duration_ms=self._elapsed_ms(start_time)
                )
            
            # Create structured result
            extracted_data = self._create_extracted_data(
                parsed_data,
                documents,
                llm_response
            )
            
            result = ExtractionResult(
                success=True,
                data=extracted_data,
                extraction_duration_ms=self._elapsed_ms(start_time)
            )
            
            # Cache the result
            if self.use_cache and self.cache:
                self._cache_result(country, documents, result)
            
            logger.info(
                f"Successfully extracted {self.parameter_name} for {country} "
                f"(confidence: {extracted_data.confidence:.2f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Extraction failed for {self.parameter_name} - {country}: {e}",
                exc_info=True
            )
            return ExtractionResult(
                success=False,
                error=str(e),
                extraction_duration_ms=self._elapsed_ms(start_time)
            )
    
    def _prepare_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare and combine document content.
        
        Args:
            documents: List of documents with 'content' and 'metadata'
            
        Returns:
            Combined document content string
        """
        combined = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            source = metadata.get('source', f'Document {i}')
            combined.append(f"--- {source} ---\n{content}\n")
        
        return "\n".join(combined)
    
    def _invoke_llm_with_retry(self, prompt: str) -> str:
        """Invoke LLM with exponential backoff retry.
        
        Args:
            prompt: Prompt to send to LLM
            
        Returns:
            LLM response string
            
        Raises:
            Exception: If all retries fail
        """
        import time
        
        for attempt in range(self.max_retries):
            try:
                response = self.llm_service.invoke(prompt)
                return response
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"LLM invocation failed (attempt {attempt + 1}/{self.max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All LLM retry attempts failed: {e}")
                    raise
    
    def _create_extracted_data(
        self,
        parsed_data: Dict[str, Any],
        documents: List[Dict[str, Any]],
        llm_response: str
    ) -> ExtractedData:
        """Create ExtractedData object from parsed results.
        
        Args:
            parsed_data: Parsed data dictionary
            documents: Source documents
            llm_response: Raw LLM response
            
        Returns:
            ExtractedData instance
        """
        # Extract sources
        sources = [
            {
                'title': doc.get('metadata', {}).get('title', 'Unknown'),
                'url': doc.get('metadata', {}).get('url', ''),
                'type': doc.get('metadata', {}).get('type', 'document')
            }
            for doc in documents
        ]
        
        # Determine confidence level
        confidence = parsed_data.get('confidence', 0.5)
        if confidence >= 0.8:
            confidence_level = ExtractionConfidence.HIGH
        elif confidence >= 0.5:
            confidence_level = ExtractionConfidence.MEDIUM
        else:
            confidence_level = ExtractionConfidence.LOW
        
        return ExtractedData(
            parameter_name=self.parameter_name,
            value=parsed_data.get('value'),
            confidence=confidence,
            confidence_level=confidence_level,
            justification=parsed_data.get('justification', ''),
            sources=sources,
            extracted_quotes=parsed_data.get('quotes', []),
            metadata={
                'llm_model': self.llm_service.model_name,
                'extraction_method': 'ai_powered',
                **parsed_data.get('metadata', {})
            }
        )
    
    def _check_cache(
        self,
        country: str,
        documents: List[Dict[str, Any]]
    ) -> Optional[ExtractionResult]:
        """Check cache for existing extraction result.
        
        Args:
            country: Country name
            documents: Documents being analyzed
            
        Returns:
            Cached ExtractionResult if found, None otherwise
        """
        if not self.cache:
            return None
        
        cache_key = self._generate_cache_key(country, documents)
        cached = self.cache.get(cache_key)
        
        if cached:
            cached.cached = True
            return cached
        
        return None
    
    def _cache_result(
        self,
        country: str,
        documents: List[Dict[str, Any]],
        result: ExtractionResult
    ):
        """Cache extraction result.
        
        Args:
            country: Country name
            documents: Documents analyzed
            result: Result to cache
        """
        if not self.cache:
            return
        
        cache_key = self._generate_cache_key(country, documents)
        self.cache.set(cache_key, result, ttl=self.cache_ttl)
    
    def _generate_cache_key(
        self,
        country: str,
        documents: List[Dict[str, Any]]
    ) -> str:
        """Generate cache key for extraction.
        
        Args:
            country: Country name
            documents: Documents being analyzed
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Include parameter, country, and document hashes
        doc_hashes = []
        for doc in documents:
            content = doc.get('content', '')
            doc_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            doc_hashes.append(doc_hash)
        
        key_parts = [
            self.parameter_name,
            country.lower().replace(' ', '_'),
            '_'.join(sorted(doc_hashes))
        ]
        
        return ':'.join(key_parts)
    
    def _elapsed_ms(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds.
        
        Args:
            start_time: Start datetime
            
        Returns:
            Elapsed time in milliseconds
        """
        delta = datetime.now() - start_time
        return delta.total_seconds() * 1000
    
    def get_required_documents(self) -> List[str]:
        """Get list of required document types for this parameter.
        
        Returns:
            List of document type identifiers
        """
        # Default implementation - subclasses can override
        return []
    
    def get_recommended_sources(self, country: str) -> List[Dict[str, str]]:
        """Get recommended data sources for this parameter.
        
        Args:
            country: Country name
            
        Returns:
            List of recommended sources with URLs
        """
        # Default implementation - subclasses can override
        return []
