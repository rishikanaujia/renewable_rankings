"""Langfuse Integration - Optional observability for research system

Provides prompt tracking, generation monitoring, and cost analysis via Langfuse.

This is completely optional and requires:
1. pip install langfuse
2. LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in environment
3. langfuse.enabled: true in research_config.yaml
"""

from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Langfuse
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.debug("Langfuse not available (pip install langfuse to enable)")


class LangfuseTracker:
    """Tracks research system operations with Langfuse."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Langfuse tracker.

        Args:
            config: Langfuse configuration from research_config.yaml
        """
        self.config = config or {}
        self.enabled = (
            LANGFUSE_AVAILABLE
            and self.config.get('enabled', False)
            and self._check_credentials()
        )

        if self.enabled:
            self.client = self._initialize_client()
            logger.info("Langfuse tracking enabled")
        else:
            self.client = None
            if not LANGFUSE_AVAILABLE:
                logger.debug("Langfuse tracking disabled (not installed)")
            elif not self.config.get('enabled', False):
                logger.debug("Langfuse tracking disabled (config)")
            else:
                logger.warning("Langfuse tracking disabled (missing credentials)")

    def _check_credentials(self) -> bool:
        """Check if Langfuse credentials are available.

        Returns:
            True if credentials are set
        """
        public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        secret_key = os.getenv('LANGFUSE_SECRET_KEY')

        return bool(public_key and secret_key)

    def _initialize_client(self) -> Optional[Any]:
        """Initialize Langfuse client.

        Returns:
            Langfuse client or None
        """
        try:
            client = Langfuse(
                public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
                secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
                host=self.config.get('host', 'https://cloud.langfuse.com')
            )
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            return None

    def track_research_generation(
        self,
        parameter: str,
        country: str,
        period: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Track a research generation event.

        Args:
            parameter: Parameter name
            country: Country name
            period: Time period
            prompt: Research prompt
            response: LLM response
            metadata: Additional metadata

        Returns:
            Trace ID or None
        """
        if not self.enabled or not self.client:
            return None

        try:
            session_id = self._format_session_id(parameter, country, period)

            trace = self.client.trace(
                name="research_generation",
                session_id=session_id,
                metadata={
                    'parameter': parameter,
                    'country': country,
                    'period': period,
                    **(metadata or {})
                }
            )

            # Track the generation
            generation = trace.generation(
                name="llm_research",
                model=metadata.get('model', 'unknown') if metadata else 'unknown',
                input=prompt,
                output=response,
                metadata=metadata or {}
            )

            logger.debug(f"Tracked research generation: {trace.id}")
            return trace.id

        except Exception as e:
            logger.error(f"Error tracking research generation: {e}")
            return None

    def track_prompt_generation(
        self,
        parameter: str,
        prompt_template: str,
        generated_prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Track prompt generation from template.

        Args:
            parameter: Parameter name
            prompt_template: Base template
            generated_prompt: Generated prompt
            metadata: Additional metadata

        Returns:
            Trace ID or None
        """
        if not self.enabled or not self.client:
            return None

        try:
            trace = self.client.trace(
                name="prompt_generation",
                metadata={
                    'parameter': parameter,
                    'template_length': len(prompt_template),
                    'prompt_length': len(generated_prompt),
                    **(metadata or {})
                }
            )

            logger.debug(f"Tracked prompt generation: {trace.id}")
            return trace.id

        except Exception as e:
            logger.error(f"Error tracking prompt generation: {e}")
            return None

    def track_cache_hit(
        self,
        parameter: str,
        country: str,
        version: str,
        age_days: float
    ) -> None:
        """Track cache hit event.

        Args:
            parameter: Parameter name
            country: Country name
            version: Version retrieved
            age_days: Age of cached document in days
        """
        if not self.enabled or not self.client:
            return

        try:
            self.client.score(
                name="cache_hit",
                value=1.0,
                data_type="NUMERIC",
                metadata={
                    'parameter': parameter,
                    'country': country,
                    'version': version,
                    'age_days': age_days
                }
            )

            logger.debug(f"Tracked cache hit: {parameter}/{country}")

        except Exception as e:
            logger.error(f"Error tracking cache hit: {e}")

    def track_cost(
        self,
        operation: str,
        cost_usd: float,
        tokens: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track cost of an operation.

        Args:
            operation: Operation name
            cost_usd: Cost in USD
            tokens: Token count
            metadata: Additional metadata
        """
        if not self.enabled or not self.client:
            return

        try:
            self.client.score(
                name=f"{operation}_cost",
                value=cost_usd,
                data_type="NUMERIC",
                metadata={
                    'tokens': tokens,
                    'cost_per_token': cost_usd / tokens if tokens > 0 else 0,
                    **(metadata or {})
                }
            )

            logger.debug(f"Tracked cost: {operation} = ${cost_usd:.4f}")

        except Exception as e:
            logger.error(f"Error tracking cost: {e}")

    def _format_session_id(self, parameter: str, country: str, period: str) -> str:
        """Format session ID.

        Args:
            parameter: Parameter name
            country: Country name
            period: Time period

        Returns:
            Formatted session ID
        """
        template = self.config.get('session_id_format', '{parameter}_{country}_{period}')
        return template.format(
            parameter=parameter.lower().replace(' ', '_'),
            country=country.lower().replace(' ', '_'),
            period=period.replace(' ', '_'),
            timestamp=datetime.now().strftime('%Y%m%d')
        )

    def flush(self) -> None:
        """Flush pending events to Langfuse."""
        if self.enabled and self.client:
            try:
                self.client.flush()
                logger.debug("Flushed Langfuse events")
            except Exception as e:
                logger.error(f"Error flushing Langfuse: {e}")


# Global tracker instance (lazy initialization)
_global_tracker: Optional[LangfuseTracker] = None


def get_tracker(config: Optional[Dict[str, Any]] = None) -> LangfuseTracker:
    """Get or create global Langfuse tracker.

    Args:
        config: Optional configuration (uses existing if None)

    Returns:
        LangfuseTracker instance
    """
    global _global_tracker

    if _global_tracker is None or config is not None:
        _global_tracker = LangfuseTracker(config)

    return _global_tracker


# Decorator for tracking functions (if Langfuse available)
if LANGFUSE_AVAILABLE:
    def track_research(func):
        """Decorator to track research functions with Langfuse."""
        @observe()
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
else:
    def track_research(func):
        """No-op decorator when Langfuse not available."""
        return func
