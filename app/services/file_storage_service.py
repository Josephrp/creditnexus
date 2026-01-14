"""
File storage service for deal document management.

This service handles creating deal folder structures and managing
documents within deal-specific directories. All files are encrypted
at rest using EncryptionService.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import json

from app.services.encryption_service import get_encryption_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for managing deal file storage."""
    
    def __init__(self, base_storage_path: str = "storage/deals"):
        """
        Initialize file storage service.
        
        Args:
            base_storage_path: Base path for deal storage (relative to project root)
        """
        self.base_storage_path = Path(base_storage_path)
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
    
    def create_deal_folder(self, user_id: int, deal_id: str) -> str:
        """
        Create folder structure for a deal.
        
        Structure: storage/deals/{user_id}/{deal_id}/
        Subdirectories: documents/, extractions/, generated/, notes/, events/
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier
            
        Returns:
            Path to the created deal folder
        """
        deal_folder = self.base_storage_path / str(user_id) / deal_id
        
        # Create main deal folder
        deal_folder.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["documents", "extractions", "generated", "notes", "events"]
        for subdir in subdirs:
            (deal_folder / subdir).mkdir(exist_ok=True)
        
        folder_path = str(deal_folder.absolute())
        logger.info(f"Created deal folder structure: {folder_path}")
        
        return folder_path
    
    def store_deal_document(
        self,
        user_id: int,
        deal_id: str,
        document_id: int,
        filename: str,
        content: bytes,
        subdirectory: str = "documents"
    ) -> str:
        """
        Store a document in the deal folder.
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier
            document_id: ID of the document
            filename: Name of the file to store
            content: File content as bytes
            subdirectory: Subdirectory to store in (documents, extractions, generated, notes)
            
        Returns:
            Path to the stored file
        """
        deal_folder = self.base_storage_path / str(user_id) / deal_id
        
        # Ensure deal folder exists
        if not deal_folder.exists():
            self.create_deal_folder(user_id, deal_id)
        
        # Determine subdirectory
        if subdirectory not in ["documents", "extractions", "generated", "notes", "events"]:
            subdirectory = "documents"
        
        target_dir = deal_folder / subdirectory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Store file with document_id prefix to avoid conflicts
        file_path = target_dir / f"{document_id}_{filename}"
        
        # Encrypt file content before storing
        if settings.ENCRYPTION_ENABLED:
            try:
                encryption_service = get_encryption_service()
                encrypted_content = encryption_service.encrypt(content)
                
                if encrypted_content is not None:
                    # Store encrypted content with .encrypted extension
                    encrypted_file_path = target_dir / f"{document_id}_{filename}.encrypted"
                    with open(encrypted_file_path, 'wb') as f:
                        f.write(encrypted_content)
                    logger.info(f"Stored encrypted document {document_id} to {encrypted_file_path}")
                    return str(encrypted_file_path.absolute())
                else:
                    logger.warning(f"Encryption returned None for document {document_id}, storing as plain text")
            except Exception as e:
                logger.error(f"Failed to encrypt file {filename}: {e}")
                if settings.ENCRYPTION_ENABLED:
                    raise ValueError(f"File encryption failed and ENCRYPTION_ENABLED=True: {e}")
        
        # Fallback: store as plain text (development mode or encryption disabled)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Stored document {document_id} to {file_path}")
        
        return str(file_path.absolute())
    
    def get_deal_documents(
        self,
        user_id: int,
        deal_id: str,
        subdirectory: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all documents for a deal.
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier
            subdirectory: Optional subdirectory to filter by
            
        Returns:
            List of document metadata dictionaries
        """
        deal_folder = self.base_storage_path / str(user_id) / deal_id
        
        if not deal_folder.exists():
            return []
        
        documents = []
        
        # Determine which subdirectories to search
        if subdirectory:
            subdirs = [subdirectory] if subdirectory in ["documents", "extractions", "generated", "notes", "events"] else ["documents"]
        else:
            subdirs = ["documents", "extractions", "generated", "notes", "events"]
        
        for subdir in subdirs:
            subdir_path = deal_folder / subdir
            if subdir_path.exists():
                for file_path in subdir_path.iterdir():
                    if file_path.is_file():
                        stat = file_path.stat()
                        # Remove .encrypted extension from display name
                        display_name = file_path.name
                        if display_name.endswith('.encrypted'):
                            display_name = display_name[:-9]  # Remove .encrypted
                        documents.append({
                            "filename": display_name,
                            "path": str(file_path.absolute()),
                            "subdirectory": subdir,
                            "size": stat.st_size,
                            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "encrypted": file_path.name.endswith('.encrypted'),
                        })
        
        return documents
    
    def get_document_path(
        self,
        user_id: int,
        deal_id: Optional[str] = None,
        document_id: int = None
    ) -> Optional[str]:
        """
        Get the file path for a specific document.
        
        Documents are stored as: storage/deals/{user_id}/{deal_id}/documents/{document_id}_{filename}
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier (optional, if None, searches in user's root)
            document_id: ID of the document
            
        Returns:
            Absolute path to the document file, or None if not found
        """
        if deal_id:
            # Search in deal-specific folder
            deal_folder = self.base_storage_path / str(user_id) / deal_id
            documents_dir = deal_folder / "documents"
        else:
            # Search in user's root documents folder (if it exists)
            user_folder = self.base_storage_path / str(user_id)
            documents_dir = user_folder / "documents"
        
        if not documents_dir.exists():
            return None
        
        # Search for files starting with {document_id}_
        # Check both encrypted and plain text files
        pattern = f"{document_id}_*"
        matching_files = list(documents_dir.glob(pattern))
        
        # Also check for encrypted files
        encrypted_pattern = f"{document_id}_*.encrypted"
        matching_files.extend(documents_dir.glob(encrypted_pattern))
        
        if matching_files:
            # Return the first match (or most recent if multiple)
            # Sort by modification time, most recent first
            matching_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return str(matching_files[0].absolute())
        
        return None
    
    def archive_deal(self, user_id: int, deal_id: str) -> str:
        """
        Archive a deal by moving it to an archive folder.
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier
            
        Returns:
            Path to the archived deal folder
        """
        deal_folder = self.base_storage_path / str(user_id) / deal_id
        archive_folder = self.base_storage_path / "archive" / str(user_id) / deal_id
        
        if not deal_folder.exists():
            logger.warning(f"Deal folder does not exist: {deal_folder}")
            return str(archive_folder.absolute())
        
        # Create archive directory structure
        archive_folder.parent.mkdir(parents=True, exist_ok=True)
        
        # Move deal folder to archive
        import shutil
        shutil.move(str(deal_folder), str(archive_folder))
        
        logger.info(f"Archived deal {deal_id} to {archive_folder}")
        
        return str(archive_folder.absolute())
    
    def store_deal_note(
        self,
        user_id: int,
        deal_id: str,
        note_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a note for a deal.
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier
            note_id: ID of the note
            content: Note content
            metadata: Optional metadata (author, timestamp, etc.)
            
        Returns:
            Path to the stored note file
        """
        deal_folder = self.base_storage_path / str(user_id) / deal_id
        
        # Ensure deal folder exists
        if not deal_folder.exists():
            self.create_deal_folder(user_id, deal_id)
        
        notes_dir = deal_folder / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        
        # Store note as JSON file (encrypted)
        note_data = {
            "note_id": note_id,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        note_file = notes_dir / f"{note_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Encrypt note content before storing
        if settings.ENCRYPTION_ENABLED:
            try:
                encryption_service = get_encryption_service()
                json_str = json.dumps(note_data, indent=2)
                encrypted_content = encryption_service.encrypt(json_str)
                
                if encrypted_content is not None:
                    encrypted_file = notes_dir / f"{note_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json.encrypted"
                    with open(encrypted_file, 'wb') as f:
                        f.write(encrypted_content)
                    logger.info(f"Stored encrypted note {note_id} to {encrypted_file}")
                    return str(encrypted_file.absolute())
                else:
                    logger.warning(f"Encryption returned None for note {note_id}, storing as plain text")
            except Exception as e:
                logger.error(f"Failed to encrypt note {note_id}: {e}")
                if settings.ENCRYPTION_ENABLED:
                    raise ValueError(f"Note encryption failed and ENCRYPTION_ENABLED=True: {e}")
        
        # Fallback: store as plain JSON (development mode or encryption disabled)
        with open(note_file, 'w', encoding='utf-8') as f:
            json.dump(note_data, f, indent=2)
        
        logger.info(f"Stored note {note_id} to {note_file}")
        
        return str(note_file.absolute())
    
    def store_cdm_event(
        self,
        user_id: int,
        deal_id: str,
        event_id: str,
        event_data: Dict[str, Any]
    ) -> str:
        """
        Store a CDM event for a deal.
        
        Args:
            user_id: ID of the user/applicant
            deal_id: Unique deal identifier
            event_id: Unique event identifier
            event_data: CDM event data dictionary
            
        Returns:
            Path to the stored event file
        """
        deal_folder = self.base_storage_path / str(user_id) / deal_id
        
        # Ensure deal folder exists
        if not deal_folder.exists():
            self.create_deal_folder(user_id, deal_id)
        
        events_dir = deal_folder / "events"
        events_dir.mkdir(parents=True, exist_ok=True)
        
        # Store event as JSON file (encrypted)
        event_file = events_dir / f"{event_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Encrypt event content before storing
        if settings.ENCRYPTION_ENABLED:
            try:
                encryption_service = get_encryption_service()
                json_str = json.dumps(event_data, indent=2)
                encrypted_content = encryption_service.encrypt(json_str)
                
                if encrypted_content is not None:
                    encrypted_file = events_dir / f"{event_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json.encrypted"
                    with open(encrypted_file, 'wb') as f:
                        f.write(encrypted_content)
                    logger.info(f"Stored encrypted CDM event {event_id} to {encrypted_file}")
                    return str(encrypted_file.absolute())
                else:
                    logger.warning(f"Encryption returned None for event {event_id}, storing as plain text")
            except Exception as e:
                logger.error(f"Failed to encrypt event {event_id}: {e}")
                if settings.ENCRYPTION_ENABLED:
                    raise ValueError(f"Event encryption failed and ENCRYPTION_ENABLED=True: {e}")
        
        # Fallback: store as plain JSON (development mode or encryption disabled)
        with open(event_file, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, indent=2)
        
        logger.info(f"Stored CDM event {event_id} to {event_file}")
        
        return str(event_file.absolute())
    
    def read_encrypted_file(self, file_path: str) -> bytes:
        """
        Read and decrypt an encrypted file.
        
        Args:
            file_path: Path to the encrypted file
            
        Returns:
            Decrypted file content as bytes
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'rb') as f:
            content = f.read()
        
        # Check if file is encrypted (has .encrypted extension or contains encrypted data)
        if path.name.endswith('.encrypted') or settings.ENCRYPTION_ENABLED:
            try:
                encryption_service = get_encryption_service()
                decrypted = encryption_service.decrypt(content)
                
                if decrypted is None:
                    # Might be plain text file
                    return content
                
                if isinstance(decrypted, bytes):
                    return decrypted
                elif isinstance(decrypted, str):
                    return decrypted.encode('utf-8')
                else:
                    return str(decrypted).encode('utf-8')
            except Exception as e:
                logger.warning(f"Failed to decrypt file {file_path}, returning as-is: {e}")
                return content
        
        return content
    
    def read_encrypted_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and decrypt an encrypted JSON file.
        
        Args:
            file_path: Path to the encrypted JSON file
            
        Returns:
            Decrypted JSON data as dictionary
        """
        content = self.read_encrypted_file(file_path)
        
        # Try to parse as JSON
        try:
            if isinstance(content, bytes):
                json_str = content.decode('utf-8')
            else:
                json_str = str(content)
            return json.loads(json_str)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse JSON from file {file_path}: {e}")
            raise ValueError(f"File does not contain valid JSON: {e}")