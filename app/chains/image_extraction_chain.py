"""Image extraction chain using Multimodal-OCR3 Gradio Space via requests API."""

import logging
import tempfile
import base64
from pathlib import Path
from typing import Optional, List, Union
from functools import lru_cache
import requests
from PIL import Image
import io

from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageExtractionService:
    """Image OCR service using prithivMLmods/Multimodal-OCR3 Gradio Space via requests API."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        hf_token: Optional[str] = None,
    ) -> None:
        """Initialize Image OCR service.

        Args:
            api_url: Gradio Space URL (default: settings.OCR_API_URL or prithivMLmods/Multimodal-OCR3)
            hf_token: HuggingFace token for authenticated Spaces (default: settings.HUGGINGFACE_API_KEY)
        """
        default_url = (
            getattr(settings, "OCR_API_URL", None)
            or "https://prithivmlmods-multimodal-ocr3.hf.space"
        )
        self.api_url = api_url or default_url
        self.hf_token = hf_token or (
            settings.HUGGINGFACE_API_KEY.get_secret_value()
            if settings.HUGGINGFACE_API_KEY
            else None
        )

    def extract_text(
        self,
        image_path: str,
        max_retries: int = 3,
    ) -> str:
        """Extract text from image using Gradio API via requests.

        Args:
            image_path: Path to image file
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Extracted text string

        Raises:
            ValueError: If OCR extraction fails after retries
        """
        logger.info(f"Extracting text from image: {image_path}")

        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                # Prepare API endpoint
                api_endpoint = f"{self.api_url.rstrip('/')}/api/Multimodal_OCR3_generate_image"

                # Read image file
                with open(image_path, "rb") as img_file:
                    files = {
                        "files": (Path(image_path).name, img_file, "image/png")
                    }
                    data = {
                        "data": [f"file={Path(image_path).name}"]
                    }

                    # Add token header if available
                    headers = {}
                    if self.hf_token:
                        headers["Authorization"] = f"Bearer {self.hf_token}"

                    # Make request to Gradio API
                    response = requests.post(
                        api_endpoint,
                        files=files,
                        data=data,
                        headers=headers,
                        timeout=300,  # 5 minute timeout for large images
                    )

                    response.raise_for_status()

                    # Extract text from response
                    result = response.json()
                    extracted_text = self._extract_text_from_result(result)

                    if not extracted_text:
                        raise ValueError("OCR returned empty text")

                    logger.info(f"Image OCR complete: {len(extracted_text)} characters")
                    return extracted_text

            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"OCR attempt {attempt + 1}/{max_retries} failed: {e}")

                if attempt < max_retries - 1:
                    logger.info("Retrying OCR...")
                    continue

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error during OCR: {e}")

                if attempt < max_retries - 1:
                    logger.info("Retrying OCR...")
                    continue

        # All retries failed
        error_msg = f"Image OCR failed after {max_retries} attempts: {last_error}"
        logger.error(error_msg)
        raise ValueError(error_msg) from last_error

    def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        filename: str = "image.png",
        max_retries: int = 3,
    ) -> str:
        """Extract text from image bytes.

        Args:
            image_bytes: Image file content as bytes
            filename: Filename for the image (default: "image.png")
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Extracted text string

        Raises:
            ValueError: If OCR extraction fails
        """
        # Save image to temp file
        temp_path = self._save_image_temp(image_bytes, filename)

        try:
            # Extract text from the temp file
            extracted_text = self.extract_text(
                temp_path,
                max_retries=max_retries,
            )
            return extracted_text
        finally:
            # Clean up temp file
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")

    def extract_text_from_image(
        self,
        image_data: Union[Image.Image, str, bytes],
        max_retries: int = 3,
    ) -> str:
        """Extract text from image data (PIL Image, file path, or bytes).

        Args:
            image_data: Image as PIL Image, file path string, or bytes
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Extracted text string

        Raises:
            ValueError: If image data type is unsupported or extraction fails
        """
        if isinstance(image_data, str):
            # Assume it's a file path
            return self.extract_text(image_data, max_retries=max_retries)
        elif isinstance(image_data, bytes):
            # Save bytes to temp file
            return self.extract_text_from_bytes(image_data, max_retries=max_retries)
        elif isinstance(image_data, Image.Image):
            # Save PIL Image to temp file
            temp_path = self._save_pil_image_temp(image_data)
            try:
                return self.extract_text(temp_path, max_retries=max_retries)
            finally:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")

    def extract_text_from_multiple_images(
        self,
        image_data_list: List[Union[Image.Image, str, bytes]],
        max_retries: int = 3,
    ) -> List[str]:
        """Extract text from multiple images.

        Args:
            image_data_list: List of images (PIL Image, file path, or bytes)
            max_retries: Maximum number of retry attempts per image (default: 3)

        Returns:
            List of extracted text strings (one per image)
        """
        extracted_texts = []
        for idx, image_data in enumerate(image_data_list):
            try:
                logger.info(f"Processing image {idx + 1}/{len(image_data_list)}")
                text = self.extract_text_from_image(image_data, max_retries=max_retries)
                extracted_texts.append(text)
            except Exception as e:
                logger.error(f"Failed to extract text from image {idx + 1}: {e}")
                extracted_texts.append("")  # Append empty string on failure

        return extracted_texts

    def _extract_text_from_result(self, api_result: dict) -> str:
        """Extract text from API result.

        Args:
            api_result: JSON response from Gradio API

        Returns:
            Extracted text string
        """
        # Gradio API typically returns: {"data": [result], ...}
        # The result might be a string, tuple, or dict
        try:
            if isinstance(api_result, dict) and "data" in api_result:
                data = api_result["data"]
                if isinstance(data, list) and len(data) > 0:
                    result = data[0]

                    # Try to extract text from result
                    if isinstance(result, str):
                        return result.strip()
                    elif isinstance(result, (list, tuple)):
                        # Try to find text in tuple/list
                        for item in result:
                            if isinstance(item, str):
                                return item.strip()
                            elif isinstance(item, dict):
                                if "text" in item:
                                    return str(item["text"]).strip()
                                if "content" in item:
                                    return str(item["content"]).strip()
                    elif isinstance(result, dict):
                        if "text" in result:
                            return str(result["text"]).strip()
                        if "content" in result:
                            return str(result["content"]).strip()

            # Fallback: try to extract from string representation
            if api_result is not None:
                text = str(api_result).strip()
                if text and text != "None" and text != "{}":
                    return text

            logger.warning(f"Could not extract text from API result: {type(api_result)}")
            return ""

        except Exception as e:
            logger.error(f"Error extracting text from result: {e}")
            return ""

    def _save_image_temp(self, image_bytes: bytes, filename: str) -> str:
        """Save image bytes to temporary file.

        Args:
            image_bytes: Image file content as bytes
            filename: Original filename (for extension detection)

        Returns:
            Path to temporary file
        """
        # Create temp file with appropriate extension
        suffix = Path(filename).suffix or ".png"
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        )
        temp_path = temp_file.name
        temp_file.write(image_bytes)
        temp_file.close()

        logger.debug(f"Saved image to temp file: {temp_path}")
        return temp_path

    def _save_pil_image_temp(self, image: Image.Image) -> str:
        """Save PIL Image to temporary file.

        Args:
            image: PIL Image object

        Returns:
            Path to temporary image file
        """
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
        )
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Save image as PNG
            image.save(temp_path, "PNG")
            logger.debug(f"Saved PIL image to temp file: {temp_path}, size={image.size}")
            return temp_path
        except Exception as e:
            logger.error(f"Failed to save PIL image to temp file: {e}")
            raise ValueError(f"Failed to save image to temp file: {e}") from e


@lru_cache(maxsize=1)
def get_image_extraction_service() -> ImageExtractionService:
    """Get or create singleton image extraction service instance.

    Returns:
        ImageExtractionService instance
    """
    return ImageExtractionService()


def create_image_extraction_chain() -> ImageExtractionService:
    """Create image extraction chain instance.

    Returns:
        ImageExtractionService instance
    """
    return get_image_extraction_service()


def process_image_file(
    image_bytes: bytes,
    filename: str = "image.png",
) -> str:
    """Process image file and return extracted text.

    Convenience function that creates an extraction service and processes the image.

    Args:
        image_bytes: Image file content as bytes
        filename: Original filename (for extension detection)

    Returns:
        Extracted text string

    Raises:
        ValueError: If extraction fails
    """
    service = get_image_extraction_service()
    return service.extract_text_from_bytes(
        image_bytes=image_bytes,
        filename=filename,
    )


def process_multiple_image_files(
    image_files: List[tuple[bytes, str]],
) -> List[str]:
    """Process multiple image files and return extracted text.

    Convenience function for batch processing.

    Args:
        image_files: List of tuples (image_bytes, filename)

    Returns:
        List of extracted text strings (one per image)
    """
    service = get_image_extraction_service()
    extracted_texts = []
    
    for image_bytes, filename in image_files:
        try:
            text = service.extract_text_from_bytes(
                image_bytes=image_bytes,
                filename=filename,
            )
            extracted_texts.append(text)
        except Exception as e:
            logger.error(f"Failed to process image {filename}: {e}")
            extracted_texts.append("")
    
    return extracted_texts











