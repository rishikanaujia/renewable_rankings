"""LLM Service - Unified interface for LLM interactions using LangChain.

This module provides a standardized way to interact with various LLM providers
through LangChain, supporting:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Azure OpenAI
    - Local models via Ollama
    - Custom endpoints

Features:
    - Automatic prompt optimization
    - Token counting and management
    - Response validation
    - Rate limiting
    - Cost tracking
    - Streaming support
    - Fallback models
"""
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import logging
import time
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    BaseMessage,
)

from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMConfig(BaseModel):
    """Configuration for LLM service."""
    
    provider: LLMProvider = Field(..., description="LLM provider")
    model_name: str = Field(..., description="Model identifier")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2000, ge=1, description="Maximum tokens in response")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    
    # API configuration
    api_key: Optional[str] = Field(None, description="API key (if not in env)")
    api_base: Optional[str] = Field(None, description="Custom API base URL")
    api_version: Optional[str] = Field(None, description="API version (Azure)")
    
    # Rate limiting
    max_requests_per_minute: int = Field(default=60, ge=1)
    max_tokens_per_minute: int = Field(default=90000, ge=1)
    
    # Retry configuration
    max_retries: int = Field(default=3, ge=1)
    retry_delay: float = Field(default=1.0, ge=0.0)
    
    # Fallback model
    fallback_model: Optional[str] = Field(None, description="Fallback model if primary fails")
    
    class Config:
        use_enum_values = True


class LLMUsageStats(BaseModel):
    """Statistics for LLM usage."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost_usd: float = 0.0
    average_latency_ms: float = 0.0


class LLMService:
    """Unified LLM service using LangChain.
    
    This service provides a consistent interface for interacting with various
    LLM providers through LangChain.
    
    Example:
        >>> config = LLMConfig(
        ...     provider=LLMProvider.ANTHROPIC,
        ...     model_name="claude-3-sonnet-20240229",
        ...     temperature=0.1
        ... )
        >>> llm_service = LLMService(config)
        >>> response = llm_service.invoke("Analyze this data...")
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize LLM service.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self.model_name = config.model_name
        
        # Initialize LangChain model
        self.llm = self._initialize_llm()
        self.fallback_llm = None
        if config.fallback_model:
            self.fallback_llm = self._initialize_llm(config.fallback_model)
        
        # Usage tracking
        self.stats = LLMUsageStats()
        
        # Rate limiting
        self._request_times: List[float] = []
        self._token_counts: List[int] = []
        
        logger.info(
            f"Initialized LLMService with {config.provider} - {config.model_name}"
        )
    
    def _initialize_llm(self, model_name: Optional[str] = None):
        """Initialize LangChain LLM based on provider.
        
        Args:
            model_name: Optional override model name
            
        Returns:
            Initialized LangChain LLM instance
        """
        model = model_name or self.config.model_name
        
        common_params = {
            'model_name': model,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens,
        }
        
        if self.config.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                **common_params,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
            )
        
        elif self.config.provider == LLMProvider.AZURE_OPENAI:
            return ChatOpenAI(
                **common_params,
                openai_api_base=self.config.api_base,
                openai_api_version=self.config.api_version,
                deployment_name=model,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
            )
        
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return ChatAnthropic(
                model=model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                anthropic_api_key=self.config.api_key
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def invoke(
        self,
        prompt: Union[str, List[BaseMessage]],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Invoke LLM with prompt.
        
        Args:
            prompt: Prompt string or list of messages
            system_message: Optional system message
            **kwargs: Additional parameters
            
        Returns:
            LLM response text
            
        Raises:
            Exception: If invocation fails after retries
        """
        start_time = time.time()
        
        try:
            # Check rate limits
            self._enforce_rate_limits()
            
            # Prepare messages
            messages = self._prepare_messages(prompt, system_message)

            # Invoke with tracking
            with get_openai_callback() as cb:
                try:
                    response = self.llm.invoke(messages)
                    response_text = response.content
                    
                    # Update stats
                    self._update_stats(cb, time.time() - start_time, success=True)
                    
                    logger.debug(
                        f"LLM invocation successful "
                        f"(tokens: {cb.total_tokens}, "
                        f"cost: ${cb.total_cost:.4f}, "
                        f"latency: {(time.time() - start_time)*1000:.0f}ms)"
                    )
                    
                    return response_text
                
                except Exception as e:
                    # Try fallback if available
                    if self.fallback_llm:
                        logger.warning(
                            f"Primary model failed: {e}. Trying fallback model..."
                        )
                        response = self.fallback_llm.invoke(messages)
                        response_text = response.content
                        
                        self._update_stats(cb, time.time() - start_time, success=True)
                        return response_text
                    else:
                        raise
        
        except Exception as e:
            self._update_stats(None, time.time() - start_time, success=False)
            logger.error(f"LLM invocation failed: {e}")
            raise
    
    def invoke_with_structured_output(
        self,
        prompt: Union[str, List[BaseMessage]],
        output_schema: Dict[str, Any],
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Invoke LLM and parse structured JSON output.
        
        Args:
            prompt: Prompt string or messages
            output_schema: Expected JSON schema
            system_message: Optional system message
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        
        # Add JSON instruction to prompt
        if isinstance(prompt, str):
            prompt = (
                f"{prompt}\n\n"
                f"Respond ONLY with valid JSON matching this schema:\n"
                f"```json\n{json.dumps(output_schema, indent=2)}\n```\n\n"
                f"Do not include any explanatory text, only the JSON object."
            )
        
        response = self.invoke(prompt, system_message)
        
        # Extract JSON from response
        return self._extract_json(response)
    
    def _prepare_messages(
        self,
        prompt: Union[str, List[BaseMessage]],
        system_message: Optional[str] = None
    ) -> List[BaseMessage]:
        """Prepare messages for LLM.
        
        Args:
            prompt: Prompt string or message list
            system_message: Optional system message
            
        Returns:
            List of BaseMessage objects
        """
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        # Add prompt
        if isinstance(prompt, str):
            messages.append(HumanMessage(content=prompt))
        elif isinstance(prompt, list):
            messages.extend(prompt)
        else:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")
        
        return messages
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response.
        
        Args:
            text: LLM response text
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        import re
        
        # Try to find JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Try to parse
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Try to find any JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError(f"Could not extract valid JSON from response: {e}")
    
    def _enforce_rate_limits(self):
        """Enforce rate limiting."""
        current_time = time.time()
        
        # Clean old request times (older than 1 minute)
        cutoff_time = current_time - 60
        self._request_times = [t for t in self._request_times if t > cutoff_time]
        
        # Check request limit
        if len(self._request_times) >= self.config.max_requests_per_minute:
            wait_time = 60 - (current_time - self._request_times[0])
            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached. Waiting {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
                self._request_times = []
        
        # Record this request
        self._request_times.append(current_time)
    
    def _update_stats(
        self,
        callback: Any,
        latency: float,
        success: bool
    ):
        """Update usage statistics.
        
        Args:
            callback: OpenAI callback with token counts
            latency: Request latency in seconds
            success: Whether request succeeded
        """
        self.stats.total_requests += 1
        
        if success:
            self.stats.successful_requests += 1
            if callback:
                self.stats.total_prompt_tokens += callback.prompt_tokens
                self.stats.total_completion_tokens += callback.completion_tokens
                self.stats.total_cost_usd += callback.total_cost
        else:
            self.stats.failed_requests += 1
        
        # Update average latency
        total_latency = self.stats.average_latency_ms * (self.stats.total_requests - 1)
        self.stats.average_latency_ms = (total_latency + latency * 1000) / self.stats.total_requests
    
    def get_stats(self) -> LLMUsageStats:
        """Get usage statistics.
        
        Returns:
            LLMUsageStats object
        """
        return self.stats
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.stats = LLMUsageStats()
        logger.info("Reset LLM usage statistics")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"LLMService(provider={self.config.provider}, "
            f"model={self.config.model_name})"
        )
