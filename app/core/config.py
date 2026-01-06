"""Configuration management using pydantic-settings for type-safe environment variables."""

from enum import Enum
from pathlib import Path
from typing import Optional, List
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    VLLM = "vllm"
    HUGGINGFACE = "huggingface"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    This class provides a typed interface to environment variables,
    ensuring that required configuration (like API keys) is present
    at startup time. If a required key is missing, the application
    will fail fast rather than failing halfway through a transaction.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Existing OpenAI settings
    OPENAI_API_KEY: SecretStr
    
    # Sentinel Hub credentials for satellite imagery
    SENTINELHUB_KEY: Optional[SecretStr] = None
    SENTINELHUB_SECRET: Optional[SecretStr] = None
    
    # LLM Provider Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI
    LLM_MODEL: str = "gpt-4o"  # Default model name
    LLM_TEMPERATURE: float = 0.0
    
    # vLLM-specific settings
    VLLM_BASE_URL: Optional[str] = None  # e.g., "http://localhost:8000"
    VLLM_API_KEY: Optional[SecretStr] = None  # Optional, for auth
    
    # HuggingFace-specific settings
    HUGGINGFACE_API_KEY: Optional[SecretStr] = None
    HUGGINGFACE_BASE_URL: Optional[str] = None  # Defaults to https://api-inference.huggingface.co/v1
    # For HuggingFace Inference Providers (Cohere, fal, etc.):
    # Use HUGGINGFACE_BASE_URL=router.huggingface.co/{provider}/v3/openai
    
    # Embeddings settings
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    EMBEDDINGS_PROVIDER: Optional[LLMProvider] = None  # If None, uses LLM_PROVIDER
    
    # Policy Engine Configuration
    POLICY_ENABLED: bool = True  # Feature flag to enable/disable policy engine
    POLICY_RULES_DIR: Path = Path("app/policies")  # Directory containing YAML policy files
    POLICY_RULES_PATTERN: str = "*.yaml"  # File pattern for policy rule files
    POLICY_ENGINE_VENDOR: Optional[str] = None  # Policy engine implementation (e.g., "aspasia", "custom")
    POLICY_AUTO_RELOAD: bool = False  # Auto-reload policies on file change (development only)
    
    # x402 Payment Engine Configuration
    X402_ENABLED: bool = True  # Feature flag to enable/disable x402 payments
    X402_FACILITATOR_URL: str = "https://facilitator.x402.org"  # x402 facilitator service URL
    X402_NETWORK: str = "base"  # Blockchain network (base, ethereum, etc.)
    X402_TOKEN: str = "USDC"  # Token symbol (USDC, USDT, etc.)
    
    # Audio Transcription (STT) Configuration
    STT_API_URL: Optional[str] = None  # Gradio Space URL (default: nvidia/canary-1b-v2)
    STT_SOURCE_LANG: str = "en"  # Source language code for transcription
    STT_TARGET_LANG: str = "en"  # Target language code for transcription
    
    # Image OCR Configuration
    OCR_API_URL: Optional[str] = None  # Gradio Space URL (default: prithivMLmods/Multimodal-OCR3)
    
    # ChromaDB Configuration
    CHROMADB_PERSIST_DIR: str = "./chroma_db"  # Directory to persist ChromaDB data
    
    @field_validator('LLM_PROVIDER', mode='before')
    @classmethod
    def validate_llm_provider(cls, v):
        """Validate LLM provider configuration."""
        if isinstance(v, str):
            try:
                return LLMProvider(v.lower())
            except ValueError:
                raise ValueError(f"Invalid LLM_PROVIDER: {v}. Must be one of: {[p.value for p in LLMProvider]}")
        return v
    
    @field_validator('POLICY_RULES_DIR', mode='before')
    @classmethod
    def validate_policy_rules_dir(cls, v):
        """Convert string path to Path object."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    def get_policy_rules_files(self) -> List[Path]:
        """
        Get list of policy rule YAML files from configured directory.
        
        Returns:
            List of Path objects for policy rule files
        """
        if not self.POLICY_ENABLED:
            return []
        
        rules_dir = Path(self.POLICY_RULES_DIR)
        if not rules_dir.exists():
            return []
        
        # Find all YAML files matching the pattern
        pattern = self.POLICY_RULES_PATTERN
        rule_files = list(rules_dir.glob(pattern))
        
        # Also check for .yml extension
        if pattern.endswith('.yaml'):
            rule_files.extend(rules_dir.glob(pattern.replace('.yaml', '.yml')))
        
        return sorted(rule_files)  # Sort for deterministic loading order
    
    def get_secret_value(self, key: str) -> str:
        """Get the secret value for a given key."""
        if key == "OPENAI_API_KEY":
            return self.OPENAI_API_KEY.get_secret_value()
        elif key == "VLLM_API_KEY" and self.VLLM_API_KEY:
            return self.VLLM_API_KEY.get_secret_value()
        elif key == "HUGGINGFACE_API_KEY" and self.HUGGINGFACE_API_KEY:
            return self.HUGGINGFACE_API_KEY.get_secret_value()
        raise ValueError(f"Unknown secret key: {key}")


# Global settings object
settings = Settings()

