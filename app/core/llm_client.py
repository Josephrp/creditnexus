"""
LLM Client Abstraction for CreditNexus.

Provides a unified interface for multiple LLM providers (OpenAI, vLLM, HuggingFace)
while maintaining LangChain compatibility. All LLM operations should use this
abstraction instead of directly instantiating provider-specific clients.
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)

# Global LLM configuration (set at startup)
_llm_config: Optional[Dict[str, Any]] = None


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    VLLM = "vllm"
    HUGGINGFACE = "huggingface"


def create_chat_model(
    provider: str,
    model: str,
    temperature: float = 0,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """
    Create a LangChain chat model using the specified provider.
    
    Uses LangChain's native provider support:
    - OpenAI: Uses langchain_openai.ChatOpenAI
    - vLLM: Uses ChatOpenAI with base_url pointing to vLLM server
    - HuggingFace: Uses ChatOpenAI with HF Inference Providers API endpoint
    
    Args:
        provider: One of 'openai', 'vllm', 'huggingface'
        model: Model identifier (e.g., 'gpt-4o', 'meta-llama/Llama-2-7b-chat-hf')
        temperature: Sampling temperature
        api_key: API key for authentication
        base_url: Base URL for API (required for vLLM, optional for others)
        **kwargs: Additional provider-specific arguments
    
    Returns:
        BaseChatModel instance compatible with LangChain
        
    Raises:
        ValueError: If provider is unsupported or required configuration is missing
    """
    provider_lower = provider.lower()
    
    if provider_lower == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            **kwargs
        )
    elif provider_lower == "vllm":
        if not base_url:
            raise ValueError("VLLM_BASE_URL is required for vLLM provider")
        # vLLM exposes OpenAI-compatible API at /v1/chat/completions
        # Ensure base_url ends with /v1
        vllm_base_url = base_url.rstrip('/')
        if not vllm_base_url.endswith('/v1'):
            vllm_base_url = f"{vllm_base_url}/v1"
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            base_url=vllm_base_url,
            api_key=api_key,  # Optional, for auth if vLLM server requires it
            **kwargs
        )
    elif provider_lower == "huggingface":
        # HuggingFace Inference Providers API uses OpenAI-compatible endpoint
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY is required for HuggingFace provider")
        
        # Extract provider from model if in format "provider/model-name"
        # Otherwise use default HF endpoint
        if base_url:
            hf_base_url = base_url
        else:
            # Default to HuggingFace Inference Providers router
            # For direct HF models, use: https://api-inference.huggingface.co/v1
            # For HF Inference Providers (Cohere, fal, etc.), use router endpoint
            hf_base_url = "https://api-inference.huggingface.co/v1"
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            base_url=hf_base_url,
            api_key=api_key,
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Must be one of: {[p.value for p in LLMProvider]}")


def create_embeddings_model(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    **kwargs
) -> Embeddings:
    """
    Create a LangChain embeddings model using the specified provider.
    
    Args:
        provider: One of 'openai', 'huggingface'
        model: Model identifier
        api_key: API key for authentication
        **kwargs: Additional provider-specific arguments
    
    Returns:
        Embeddings instance compatible with LangChain
        
    Raises:
        ValueError: If provider is unsupported or required configuration is missing
    """
    provider_lower = provider.lower()
    
    if provider_lower == "openai":
        return OpenAIEmbeddings(
            model=model,
            openai_api_key=api_key,
            **kwargs
        )
    elif provider_lower == "huggingface":
        # Use langchain_huggingface for native HF embeddings support
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name=model,
                **kwargs
            )
        except ImportError:
            # Fallback: Use OpenAI-compatible endpoint if langchain_huggingface not available
            logger.warning(
                "langchain_huggingface not available, using OpenAI-compatible endpoint for HuggingFace embeddings"
            )
            return OpenAIEmbeddings(
                model=model,
                base_url="https://api-inference.huggingface.co/v1",
                openai_api_key=api_key,
                **kwargs
            )
    else:
        raise ValueError(f"Unsupported embeddings provider: {provider}. Must be one of: 'openai', 'huggingface'")


def init_llm_config(settings) -> None:
    """
    Initialize global LLM configuration from settings.
    
    This is called once at application startup. It validates provider-specific
    settings and stores the configuration globally for use by get_chat_model()
    and get_embeddings_model().
    
    Args:
        settings: Application settings object (from app.core.config)
        
    Raises:
        ValueError: If required configuration is missing for the selected provider
        RuntimeError: If configuration is invalid
    """
    global _llm_config
    
    # Validate provider-specific settings
    provider = settings.LLM_PROVIDER.value if hasattr(settings.LLM_PROVIDER, 'value') else settings.LLM_PROVIDER
    
    if provider == "vllm" and not settings.VLLM_BASE_URL:
        raise ValueError("VLLM_BASE_URL is required when LLM_PROVIDER=vllm")
    
    if provider == "huggingface" and not settings.HUGGINGFACE_API_KEY:
        raise ValueError("HUGGINGFACE_API_KEY is required when LLM_PROVIDER=huggingface")
    
    # Get API key for provider
    api_key = _get_api_key_for_provider(settings)
    
    # Get base URL for provider
    base_url = _get_base_url_for_provider(settings)
    
    # Store global configuration
    _llm_config = {
        "provider": provider,
        "model": settings.LLM_MODEL,
        "temperature": settings.LLM_TEMPERATURE,
        "api_key": api_key,
        "base_url": base_url,
    }
    
    # Embeddings configuration
    embeddings_provider = settings.EMBEDDINGS_PROVIDER
    if embeddings_provider is None:
        embeddings_provider = settings.LLM_PROVIDER
    
    embeddings_provider_value = embeddings_provider.value if hasattr(embeddings_provider, 'value') else embeddings_provider
    
    _llm_config["embeddings"] = {
        "provider": embeddings_provider_value,
        "model": settings.EMBEDDINGS_MODEL,
        "api_key": _get_embeddings_api_key(settings, embeddings_provider),
    }
    
    logger.info(
        f"LLM client configured: provider={provider}, model={settings.LLM_MODEL}, "
        f"embeddings_provider={embeddings_provider_value}, embeddings_model={settings.EMBEDDINGS_MODEL}"
    )


def _get_api_key_for_provider(settings) -> Optional[str]:
    """Get the appropriate API key for the configured provider."""
    provider = settings.LLM_PROVIDER.value if hasattr(settings.LLM_PROVIDER, 'value') else settings.LLM_PROVIDER
    
    if provider == "openai":
        return settings.OPENAI_API_KEY.get_secret_value()
    elif provider == "vllm":
        return settings.VLLM_API_KEY.get_secret_value() if settings.VLLM_API_KEY else None
    elif provider == "huggingface":
        return settings.HUGGINGFACE_API_KEY.get_secret_value() if settings.HUGGINGFACE_API_KEY else None
    return None


def _get_base_url_for_provider(settings) -> Optional[str]:
    """Get the appropriate base URL for the configured provider."""
    provider = settings.LLM_PROVIDER.value if hasattr(settings.LLM_PROVIDER, 'value') else settings.LLM_PROVIDER
    
    if provider == "vllm":
        return settings.VLLM_BASE_URL
    elif provider == "huggingface":
        return settings.HUGGINGFACE_BASE_URL
    return None


def _get_embeddings_api_key(settings, provider) -> Optional[str]:
    """Get API key for embeddings provider."""
    provider_value = provider.value if hasattr(provider, 'value') else provider
    
    if provider_value == "openai":
        return settings.OPENAI_API_KEY.get_secret_value()
    elif provider_value == "huggingface":
        return settings.HUGGINGFACE_API_KEY.get_secret_value() if settings.HUGGINGFACE_API_KEY else None
    return None


def get_chat_model(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs
) -> BaseChatModel:
    """
    Get a chat model instance using the global configuration.
    
    This is the main function to use throughout the codebase instead of
    directly instantiating ChatOpenAI.
    
    Args:
        model: Override default model (uses LLM_MODEL from config if not provided)
        temperature: Override default temperature (uses LLM_TEMPERATURE from config if not provided)
        **kwargs: Additional arguments passed to the model constructor
    
    Returns:
        BaseChatModel instance ready to use
        
    Raises:
        RuntimeError: If LLM configuration has not been initialized
    """
    if _llm_config is None:
        raise RuntimeError(
            "LLM configuration not initialized. Call init_llm_config() at startup."
        )
    
    return create_chat_model(
        provider=_llm_config["provider"],
        model=model or _llm_config["model"],
        temperature=temperature if temperature is not None else _llm_config["temperature"],
        api_key=_llm_config["api_key"],
        base_url=_llm_config["base_url"],
        **kwargs
    )


def get_embeddings_model(
    model: Optional[str] = None,
    **kwargs
) -> Embeddings:
    """
    Get an embeddings model instance using the global configuration.
    
    Args:
        model: Override default model (uses EMBEDDINGS_MODEL from config if not provided)
        **kwargs: Additional arguments passed to the embeddings constructor
    
    Returns:
        Embeddings instance ready to use
        
    Raises:
        RuntimeError: If LLM configuration has not been initialized
    """
    if _llm_config is None:
        raise RuntimeError(
            "LLM configuration not initialized. Call init_llm_config() at startup."
        )
    
    embeddings_config = _llm_config["embeddings"]
    return create_embeddings_model(
        provider=embeddings_config["provider"],
        model=model or embeddings_config["model"],
        api_key=embeddings_config["api_key"],
        **kwargs
    )








