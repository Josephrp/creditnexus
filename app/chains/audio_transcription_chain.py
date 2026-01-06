"""Audio transcription chain using nvidia/canary-1b-v2 Gradio Space via requests API."""

import logging
import tempfile
from pathlib import Path
from typing import Optional
import requests
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


class AudioTranscriptionService:
    """STT service using nvidia/canary-1b-v2 Gradio Space via requests API."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        hf_token: Optional[str] = None,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
    ) -> None:
        """Initialize STT service.

        Args:
            api_url: Gradio Space URL (default: settings.STT_API_URL or nvidia/canary-1b-v2)
            hf_token: HuggingFace token for authenticated Spaces (default: settings.HUGGINGFACE_API_KEY)
            source_lang: Source language code (default: settings.STT_SOURCE_LANG or "en")
            target_lang: Target language code (default: settings.STT_TARGET_LANG or "en")
        """
        self.api_url = api_url or getattr(settings, "STT_API_URL", None) or "https://nvidia-canary-1b-v2.hf.space"
        self.hf_token = hf_token or (settings.HUGGINGFACE_API_KEY.get_secret_value() if settings.HUGGINGFACE_API_KEY else None)
        self.source_lang = source_lang or getattr(settings, "STT_SOURCE_LANG", "en")
        self.target_lang = target_lang or getattr(settings, "STT_TARGET_LANG", "en")

    def transcribe_file(
        self,
        audio_path: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        max_retries: int = 3,
    ) -> str:
        """Transcribe audio file using Gradio API via requests.

        Args:
            audio_path: Path to audio file
            source_lang: Source language (overrides instance default)
            target_lang: Target language (overrides instance default)
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Transcribed text string

        Raises:
            ValueError: If transcription fails after retries
        """
        source_lang = source_lang or self.source_lang
        target_lang = target_lang or self.target_lang

        logger.info(
            f"Transcribing audio file: {audio_path} (source_lang={source_lang}, target_lang={target_lang})"
        )

        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                # Prepare API endpoint - Gradio Spaces use /api/{api_name} format
                api_endpoint = f"{self.api_url.rstrip('/')}/api/transcribe_file"
                
                # Prepare file for upload
                with open(audio_path, "rb") as audio_file:
                    # Gradio API expects form-data with file and parameters
                    files = {
                        "files": (Path(audio_path).name, audio_file, "audio/wav")
                    }
                    data = {
                        "data": [
                            f"file={Path(audio_path).name}",  # Gradio expects file reference
                            source_lang,
                            target_lang,
                        ]
                    }
                    
                    # Add token header if available
                    headers = {}
                    if self.hf_token:
                        headers["Authorization"] = f"Bearer {self.hf_token}"
                    
                    # Make request to Gradio API
                    # Note: Gradio API format may vary - this is a best-effort implementation
                    response = requests.post(
                        api_endpoint,
                        files=files,
                        data=data,
                        headers=headers,
                        timeout=300,  # 5 minute timeout for long audio files
                    )
                    
                    response.raise_for_status()
                    
                    # Extract transcription from response
                    # Gradio returns JSON with "data" field containing results
                    result = response.json()
                    transcribed_text = self._extract_transcription(result)
                    
                    if not transcribed_text:
                        raise ValueError("Transcription returned empty text")
                    
                    logger.info(
                        f"Audio transcription complete: {len(transcribed_text)} characters"
                    )
                    
                    return transcribed_text

            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"Transcription attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info("Retrying transcription...")
                    continue
                    
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error during transcription: {e}")
                
                if attempt < max_retries - 1:
                    logger.info("Retrying transcription...")
                    continue
        
        # All retries failed
        error_msg = f"Audio transcription failed after {max_retries} attempts: {last_error}"
        logger.error(error_msg)
        raise ValueError(error_msg) from last_error

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        max_retries: int = 3,
    ) -> str:
        """Transcribe audio bytes to text.

        Args:
            audio_bytes: Audio file content as bytes
            filename: Filename for the audio (default: "audio.wav")
            source_lang: Source language (overrides instance default)
            target_lang: Target language (overrides instance default)
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Transcribed text string

        Raises:
            ValueError: If transcription fails
        """
        # Save audio to temp file
        temp_path = self._save_audio_temp(audio_bytes, filename)

        try:
            # Transcribe the temp file
            transcribed_text = self.transcribe_file(
                temp_path,
                source_lang=source_lang,
                target_lang=target_lang,
                max_retries=max_retries,
            )
            return transcribed_text
        finally:
            # Clean up temp file
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")

    def _extract_transcription(self, api_result: dict) -> str:
        """Extract transcription text from API result.

        Args:
            api_result: JSON response from Gradio API

        Returns:
            Extracted transcription text
        """
        # Gradio API typically returns: {"data": [result_tuple], ...}
        # The result tuple is: (dataframe, csv_path, srt_path)
        try:
            if isinstance(api_result, dict) and "data" in api_result:
                data = api_result["data"]
                if isinstance(data, list) and len(data) > 0:
                    result_tuple = data[0]
                    
                    # Try to extract from dataframe first
                    if isinstance(result_tuple, list) and len(result_tuple) >= 1:
                        dataframe = result_tuple[0]
                        if isinstance(dataframe, dict) and "data" in dataframe:
                            rows = dataframe.get("data", [])
                            if rows:
                                text_segments = []
                                for row in rows:
                                    if isinstance(row, list) and len(row) > 0:
                                        text_segments.append(str(row[0]))
                                if text_segments:
                                    return " ".join(text_segments)
                    
                    # Fallback: try to read CSV file if available
                    if len(result_tuple) >= 2 and result_tuple[1]:
                        csv_path = result_tuple[1]
                        try:
                            import pandas as pd
                            df = pd.read_csv(csv_path)
                            if "text" in df.columns:
                                return " ".join(df["text"].astype(str).tolist())
                            elif len(df.columns) > 0:
                                return " ".join(df.iloc[:, 0].astype(str).tolist())
                        except Exception as e:
                            logger.warning(f"Failed to read CSV from transcription result: {e}")
            
            # Last resort: return empty string
            logger.warning(f"Could not extract transcription from API result: {type(api_result)}")
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting transcription: {e}")
            return ""

    def _save_audio_temp(self, audio_bytes: bytes, filename: str) -> str:
        """Save audio bytes to temporary file.

        Args:
            audio_bytes: Audio file content as bytes
            filename: Original filename (for extension detection)

        Returns:
            Path to temporary file
        """
        # Create temp file with appropriate extension
        suffix = Path(filename).suffix or ".wav"
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        )
        temp_path = temp_file.name
        temp_file.write(audio_bytes)
        temp_file.close()

        logger.debug(f"Saved audio to temp file: {temp_path}")
        return temp_path


@lru_cache(maxsize=1)
def get_audio_transcription_service() -> AudioTranscriptionService:
    """Get or create singleton audio transcription service instance.

    Returns:
        AudioTranscriptionService instance
    """
    return AudioTranscriptionService()


def create_audio_transcription_chain() -> AudioTranscriptionService:
    """Create audio transcription chain instance.

    Returns:
        AudioTranscriptionService instance
    """
    return get_audio_transcription_service()


def process_audio_file(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
) -> str:
    """Process audio file and return transcribed text.

    Convenience function that creates a transcription service and processes the audio.

    Args:
        audio_bytes: Audio file content as bytes
        filename: Original filename (for extension detection)
        source_lang: Source language code (optional)
        target_lang: Target language code (optional)

    Returns:
        Transcribed text string

    Raises:
        ValueError: If transcription fails
    """
    service = get_audio_transcription_service()
    return service.transcribe_bytes(
        audio_bytes=audio_bytes,
        filename=filename,
        source_lang=source_lang,
        target_lang=target_lang,
    )

