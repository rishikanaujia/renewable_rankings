"""Data Validators - Validation logic for extracted parameter data.

This module provides validation functions for ensuring extracted data
meets quality standards and business rules.

Features:
    - Score range validation (1-10)
    - Confidence threshold checking
    - Data type validation
    - Business rule enforcement
    - Custom validators per parameter
"""
from typing import Dict, Any, Tuple, Optional, List
import logging


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class DataValidator:
    """Validator for extracted parameter data.
    
    Provides validation methods for ensuring extracted data quality.
    """
    
    @staticmethod
    def validate_score(
        score: float,
        min_score: float = 1.0,
        max_score: float = 10.0,
        parameter_name: str = "unknown"
    ) -> Tuple[bool, Optional[str]]:
        """Validate score is within acceptable range.
        
        Args:
            score: Score value to validate
            min_score: Minimum acceptable score
            max_score: Maximum acceptable score
            parameter_name: Name of parameter for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(score, (int, float)):
            return False, f"{parameter_name}: Score must be numeric, got {type(score)}"
        
        if not min_score <= score <= max_score:
            return False, f"{parameter_name}: Score {score} out of range [{min_score}, {max_score}]"
        
        return True, None
    
    @staticmethod
    def validate_confidence(
        confidence: float,
        min_confidence: float = 0.0,
        parameter_name: str = "unknown"
    ) -> Tuple[bool, Optional[str]]:
        """Validate confidence score.
        
        Args:
            confidence: Confidence value (0.0-1.0)
            min_confidence: Minimum acceptable confidence
            parameter_name: Name of parameter for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(confidence, (int, float)):
            return False, f"{parameter_name}: Confidence must be numeric"
        
        if not 0.0 <= confidence <= 1.0:
            return False, f"{parameter_name}: Confidence {confidence} must be between 0.0 and 1.0"
        
        if confidence < min_confidence:
            return False, f"{parameter_name}: Confidence {confidence} below minimum {min_confidence}"
        
        return True, None
    
    @staticmethod
    def validate_justification(
        justification: str,
        min_length: int = 20,
        parameter_name: str = "unknown"
    ) -> Tuple[bool, Optional[str]]:
        """Validate justification text.
        
        Args:
            justification: Justification text
            min_length: Minimum acceptable length
            parameter_name: Name of parameter for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(justification, str):
            return False, f"{parameter_name}: Justification must be string"
        
        if len(justification.strip()) < min_length:
            return False, f"{parameter_name}: Justification too short (min {min_length} chars)"
        
        return True, None
    
    @staticmethod
    def validate_extracted_data(
        data: Dict[str, Any],
        parameter_name: str,
        required_fields: Optional[List[str]] = None,
        score_range: Tuple[float, float] = (1.0, 10.0),
        min_confidence: float = 0.0,
        min_justification_length: int = 20
    ) -> Tuple[bool, Optional[str]]:
        """Comprehensive validation of extracted data.
        
        Args:
            data: Extracted data dictionary
            parameter_name: Name of parameter
            required_fields: List of required field names
            score_range: Tuple of (min_score, max_score)
            min_confidence: Minimum acceptable confidence
            min_justification_length: Minimum justification length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if required_fields is None:
            required_fields = ['value', 'confidence', 'justification']
        
        for field in required_fields:
            if field not in data:
                return False, f"{parameter_name}: Missing required field '{field}'"
        
        # Validate value/score
        if 'value' in data:
            is_valid, error = DataValidator.validate_score(
                data['value'],
                score_range[0],
                score_range[1],
                parameter_name
            )
            if not is_valid:
                return False, error
        
        # Validate confidence
        if 'confidence' in data:
            is_valid, error = DataValidator.validate_confidence(
                data['confidence'],
                min_confidence,
                parameter_name
            )
            if not is_valid:
                return False, error
        
        # Validate justification
        if 'justification' in data:
            is_valid, error = DataValidator.validate_justification(
                data['justification'],
                min_justification_length,
                parameter_name
            )
            if not is_valid:
                return False, error
        
        return True, None
    
    @staticmethod
    def validate_percentage(
        value: float,
        parameter_name: str = "unknown",
        allow_over_100: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """Validate percentage value.
        
        Args:
            value: Percentage value
            parameter_name: Name of parameter
            allow_over_100: Whether to allow values > 100
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, f"{parameter_name}: Percentage must be numeric"
        
        max_value = 150.0 if allow_over_100 else 100.0
        
        if not 0.0 <= value <= max_value:
            return False, f"{parameter_name}: Percentage {value} out of range [0, {max_value}]"
        
        return True, None
    
    @staticmethod
    def validate_year(
        year: int,
        parameter_name: str = "unknown",
        min_year: int = 2020,
        max_year: int = 2100
    ) -> Tuple[bool, Optional[str]]:
        """Validate year value.
        
        Args:
            year: Year value
            parameter_name: Name of parameter
            min_year: Minimum acceptable year
            max_year: Maximum acceptable year
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            return False, f"{parameter_name}: Year must be integer"
        
        if not min_year <= year_int <= max_year:
            return False, f"{parameter_name}: Year {year_int} out of range [{min_year}, {max_year}]"
        
        return True, None


# Convenience functions

def validate_score(score: float, **kwargs) -> Tuple[bool, Optional[str]]:
    """Validate score value."""
    return DataValidator.validate_score(score, **kwargs)


def validate_confidence(confidence: float, **kwargs) -> Tuple[bool, Optional[str]]:
    """Validate confidence value."""
    return DataValidator.validate_confidence(confidence, **kwargs)


def validate_extracted_data(data: Dict[str, Any], **kwargs) -> Tuple[bool, Optional[str]]:
    """Validate extracted data."""
    return DataValidator.validate_extracted_data(data, **kwargs)
