"""
Utility script to load documents from a seed directory into ChromaDB on startup.

This script:
1. Scans a configurable directory for document files (text, PDF, images, audio)
2. Extracts text content from each file
3. Indexes the content in ChromaDB for semantic search
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import mimetypes

from app.core.config import settings
from app.chains.document_retrieval_chain import DocumentRetrievalService
from app.chains.extraction_chain import extract_data_smart

logger = logging.getLogger(__name__)


def load_documents_from_directory(
    seed_dir: str,
    retrieval_service: Optional[DocumentRetrievalService] = None
) -> int:
    """
    Load all documents from a seed directory into ChromaDB.
    
    Args:
        seed_dir: Directory path containing seed documents
        retrieval_service: Optional DocumentRetrievalService instance (creates new if None)
        
    Returns:
        Number of documents successfully loaded
    """
    seed_path = Path(seed_dir)
    
    if not seed_path.exists():
        logger.warning(f"Seed directory does not exist: {seed_dir}")
        return 0
    
    if not seed_path.is_dir():
        logger.warning(f"Seed path is not a directory: {seed_dir}")
        return 0
    
    # Initialize retrieval service if not provided
    if retrieval_service is None:
        try:
            retrieval_service = DocumentRetrievalService()
        except ImportError:
            logger.error("ChromaDB not available. Cannot load seed documents.")
            return 0
        except Exception as e:
            logger.error(f"Failed to initialize DocumentRetrievalService: {e}")
            return 0
    
    # Supported file extensions
    text_extensions = {'.txt', '.md', '.json'}
    document_extensions = {'.pdf', '.doc', '.docx'}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
    audio_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}
    
    all_extensions = text_extensions | document_extensions | image_extensions | audio_extensions
    
    # Find all supported files
    files = []
    for ext in all_extensions:
        files.extend(seed_path.glob(f"*{ext}"))
        files.extend(seed_path.glob(f"**/*{ext}"))  # Recursive
    
    if not files:
        logger.info(f"No supported files found in seed directory: {seed_dir}")
        return 0
    
    logger.info(f"Found {len(files)} files in seed directory: {seed_dir}")
    
    loaded_count = 0
    
    for file_path in files:
        try:
            # Determine file type
            file_ext = file_path.suffix.lower()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Read file content based on type
            if file_ext in text_extensions:
                # Text files - read directly
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                
                # Extract CDM data from text
                try:
                    extraction_result = extract_data_smart(text=text_content)
                    if extraction_result.agreement:
                        cdm_data = extraction_result.agreement.model_dump(mode='json')
                    else:
                        # If extraction fails, use raw text as CDM data
                        cdm_data = {"raw_text": text_content}
                except Exception as e:
                    logger.warning(f"Failed to extract CDM data from {file_path.name}: {e}")
                    cdm_data = {"raw_text": text_content}
            
            elif file_ext in document_extensions:
                # Document files - would need document parsing
                # For now, skip or use OCR if available
                logger.warning(f"Document file type not yet supported for direct loading: {file_path.name}")
                continue
            
            elif file_ext in image_extensions:
                # Image files - would need OCR
                # For now, skip or use OCR if available
                logger.warning(f"Image file type not yet supported for direct loading: {file_path.name}")
                continue
            
            elif file_ext in audio_extensions:
                # Audio files - would need transcription
                # For now, skip or use STT if available
                logger.warning(f"Audio file type not yet supported for direct loading: {file_path.name}")
                continue
            
            else:
                logger.warning(f"Unsupported file type: {file_path.name}")
                continue
            
            # Prepare metadata
            metadata = {
                "title": file_path.stem,
                "source_file": str(file_path),
                "file_type": file_ext[1:] if file_ext else "unknown",
                "mime_type": mime_type or "unknown",
            }
            
            # Use file path hash as document ID (since we don't have a database ID)
            import hashlib
            doc_id = int(hashlib.md5(str(file_path).encode()).hexdigest()[:8], 16) % (10**9)
            
            # Add to ChromaDB
            retrieval_service.add_document(
                document_id=doc_id,
                cdm_data=cdm_data,
                metadata=metadata
            )
            
            loaded_count += 1
            logger.info(f"Loaded seed document: {file_path.name} (ID: {doc_id})")
            
        except Exception as e:
            logger.error(f"Failed to load seed document {file_path.name}: {e}")
            continue
    
    logger.info(f"Successfully loaded {loaded_count} documents from seed directory: {seed_dir}")
    return loaded_count


def load_chroma_seeds_on_startup() -> int:
    """
    Load seed documents into ChromaDB on application startup.
    
    This function checks the CHROMADB_SEED_DOCUMENTS_DIR configuration
    and loads all documents from that directory if set.
    
    Returns:
        Number of documents loaded (0 if disabled or no directory set)
    """
    seed_dir = settings.CHROMADB_SEED_DOCUMENTS_DIR
    
    if not seed_dir:
        logger.debug("CHROMADB_SEED_DOCUMENTS_DIR not set, skipping seed document loading")
        return 0
    
    logger.info(f"Loading seed documents from: {seed_dir}")
    
    try:
        return load_documents_from_directory(seed_dir)
    except Exception as e:
        logger.error(f"Failed to load seed documents: {e}", exc_info=True)
        return 0
