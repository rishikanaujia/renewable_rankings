"""Ownership Hurdles Extractor - AI-powered extraction for foreign ownership restrictions."""
from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import re
from ..base_extractor import BaseExtractor
from ..prompts.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)

class OwnershipHurdlesExtractor(BaseExtractor):
    """Extractor for ownership hurdles parameter."""

    def _get_extraction_prompt(self, country: str, document_content: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Use simple f-string prompt
        return f"""Extract foreign ownership restrictions and barriers for renewable energy in {country}.

Analyze foreign ownership limits, regulatory approval complexity, local content requirements, and investment screening processes.

**DOCUMENTS**:
{document_content}

Respond with JSON containing: value (1-10 score), confidence, justification, quotes, metadata.

Score Guidelines (lower restrictions = higher score):
- 1-2: Prohibitive (foreign ownership banned/<10%)
- 3-4: High (25-40% foreign ownership allowed)
- 5-6: Moderate (50-65% foreign ownership allowed)
- 7-8: Low restrictions (75-85% foreign ownership allowed)
- 9-10: No barriers (100% foreign ownership allowed)

IMPORTANT: Lower ownership restrictions = Better market access = HIGHER score"""

    def _parse_llm_response(self, llm_response: str, country: str) -> Dict[str, Any]:
        try:
            parsed = self._extract_json_from_response(llm_response)
            for field in ['value', 'confidence', 'justification']:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            score = self._normalize_score_value(parsed['value'])
            if 'metadata' not in parsed:
                parsed['metadata'] = {}
            parsed['metadata']['country'] = country
            parsed['normalized_value'] = score
            logger.info(f"Parsed ownership hurdles for {country}: score={score}/10, confidence={parsed['confidence']:.2f}")
            return parsed
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            raise

    def _validate_extracted_data(self, data: Dict[str, Any], country: str) -> Tuple[bool, Optional[str]]:
        score = data.get('normalized_value', 0)
        if not 1 <= score <= 10:
            return False, f"Invalid score: {score}"
        confidence = data.get('confidence', 0)
        if not 0.0 <= confidence <= 1.0:
            return False, f"Invalid confidence: {confidence}"
        return True, None

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            json_text = match.group(1)
        else:
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response, re.DOTALL)
            json_text = match.group(0) if match else response
        return json.loads(json_text.strip())

    def _normalize_score_value(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value_clean = value.strip().replace('/10', '').strip()
            number_match = re.search(r'(\d+(?:\.\d+)?)', value_clean)
            if number_match:
                return float(number_match.group(1))
        logger.warning(f"Could not normalize score value: {value}")
        return 5.0

    def get_required_documents(self) -> List[str]:
        return ['fdi_regulations', 'ownership_restrictions', 'investment_screening_policies']
