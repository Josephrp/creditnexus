"""
Clause cache service for AI-generated clause caching.

Reduces LLM costs by caching generated clauses and reusing them when
the context is similar.
"""

import logging
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import ClauseCache, LMATemplate
from app.models.cdm import CreditAgreement

logger = logging.getLogger(__name__)


class ClauseCacheService:
    """Service for managing cached AI-generated clauses."""
    
    def __init__(self):
        """Initialize clause cache service."""
        logger.debug("ClauseCacheService initialized")
    
    def get_cached_clause(
        self,
        db: Session,
        template_id: int,
        field_name: str,
        context_hash: Optional[str] = None,
        cdm_data: Optional[CreditAgreement] = None
    ) -> Optional[ClauseCache]:
        """
        Get a cached clause if it exists.
        
        Args:
            db: Database session
            template_id: Template ID
            field_name: Field name (e.g., "REPRESENTATIONS_AND_WARRANTIES")
            context_hash: Optional context hash for exact match
            cdm_data: Optional CDM data to compute context hash if not provided
            
        Returns:
            ClauseCache instance if found, None otherwise
        """
        # Compute context hash if not provided but cdm_data is available
        if context_hash is None and cdm_data is not None:
            context_hash = self._compute_context_hash(cdm_data, field_name)
        
        # Build query
        query = db.query(ClauseCache).filter(
            and_(
                ClauseCache.template_id == template_id,
                ClauseCache.field_name == field_name
            )
        )
        
        # If context_hash is provided, use it for exact match
        # Otherwise, get the most recently used clause for this template+field
        if context_hash:
            query = query.filter(ClauseCache.context_hash == context_hash)
            clause = query.first()
        else:
            # Get most recently used clause (fallback)
            clause = query.order_by(ClauseCache.last_used_at.desc()).first()
        
        if clause:
            # Update usage statistics
            clause.usage_count += 1
            clause.last_used_at = datetime.utcnow()
            db.commit()
            logger.debug(f"Retrieved cached clause for {field_name} (usage count: {clause.usage_count})")
        
        return clause
    
    def save_clause(
        self,
        db: Session,
        template_id: int,
        field_name: str,
        clause_content: str,
        cdm_data: Optional[CreditAgreement] = None,
        context_hash: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> ClauseCache:
        """
        Save a generated clause to the cache.
        
        Args:
            db: Database session
            template_id: Template ID
            field_name: Field name (e.g., "REPRESENTATIONS_AND_WARRANTIES")
            clause_content: Generated clause content
            cdm_data: Optional CDM data for context summary and hash
            context_hash: Optional pre-computed context hash
            created_by: Optional user ID who generated the clause
            
        Returns:
            Created ClauseCache instance
        """
        # Compute context hash if not provided
        if context_hash is None and cdm_data is not None:
            context_hash = self._compute_context_hash(cdm_data, field_name)
        
        # Create context summary for display
        context_summary = None
        if cdm_data:
            context_summary = self._create_context_summary(cdm_data)
        
        # Check if clause already exists for this template+field+context
        existing_clause = None
        if context_hash:
            existing_clause = db.query(ClauseCache).filter(
                and_(
                    ClauseCache.template_id == template_id,
                    ClauseCache.field_name == field_name,
                    ClauseCache.context_hash == context_hash
                )
            ).first()
        
        if existing_clause:
            # Update existing clause
            existing_clause.clause_content = clause_content
            existing_clause.context_summary = context_summary
            existing_clause.updated_at = datetime.utcnow()
            db.commit()
            logger.debug(f"Updated cached clause for {field_name}")
            return existing_clause
        else:
            # Create new clause cache entry
            clause_cache = ClauseCache(
                template_id=template_id,
                field_name=field_name,
                clause_content=clause_content,
                context_hash=context_hash,
                context_summary=context_summary,
                usage_count=0,
                created_by=created_by
            )
            db.add(clause_cache)
            db.commit()
            db.refresh(clause_cache)
            logger.info(f"Cached clause for {field_name} (template_id: {template_id})")
            return clause_cache
    
    def _compute_context_hash(
        self,
        cdm_data: CreditAgreement,
        field_name: str
    ) -> str:
        """
        Compute a hash of the CDM context for cache key.
        
        Uses relevant CDM fields that affect clause generation:
        - Borrower name and LEI
        - Facility details (amount, currency, maturity)
        - Governing law
        - Sustainability-linked flag
        
        Args:
            cdm_data: CreditAgreement instance
            field_name: Field name for context-specific hashing
            
        Returns:
            SHA-256 hash string
        """
        # Extract relevant context fields
        context_data = {
            "field_name": field_name,
            "borrower": None,
            "facility": None,
            "governing_law": cdm_data.governing_law,
            "sustainability_linked": cdm_data.sustainability_linked,
        }
        
        # Get borrower info
        if cdm_data.parties:
            borrower = next(
                (p for p in cdm_data.parties if p.role == "Borrower"),
                None
            )
            if borrower:
                context_data["borrower"] = {
                    "name": borrower.name,
                    "lei": borrower.lei,
                }
        
        # Get facility info
        if cdm_data.facilities and len(cdm_data.facilities) > 0:
            facility = cdm_data.facilities[0]
            context_data["facility"] = {
                "amount": str(facility.commitment_amount.amount) if facility.commitment_amount else None,
                "currency": facility.commitment_amount.currency if facility.commitment_amount else None,
                "maturity_date": str(facility.maturity_date) if facility.maturity_date else None,
            }
        
        # Serialize and hash
        context_json = json.dumps(context_data, sort_keys=True)
        return hashlib.sha256(context_json.encode('utf-8')).hexdigest()
    
    def _create_context_summary(self, cdm_data: CreditAgreement) -> Dict[str, Any]:
        """
        Create a summary of CDM context for display purposes.
        
        Args:
            cdm_data: CreditAgreement instance
            
        Returns:
            Dictionary with context summary
        """
        summary = {
            "borrower_name": None,
            "facility_amount": None,
            "currency": None,
            "governing_law": cdm_data.governing_law,
        }
        
        # Get borrower name
        if cdm_data.parties:
            borrower = next(
                (p for p in cdm_data.parties if p.role == "Borrower"),
                None
            )
            if borrower:
                summary["borrower_name"] = borrower.name
        
        # Get facility amount
        if cdm_data.facilities and len(cdm_data.facilities) > 0:
            facility = cdm_data.facilities[0]
            if facility.commitment_amount:
                summary["facility_amount"] = str(facility.commitment_amount.amount)
                summary["currency"] = facility.commitment_amount.currency
        
        return summary
    
    def list_clauses(
        self,
        db: Session,
        template_id: Optional[int] = None,
        field_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[ClauseCache]:
        """
        List cached clauses with optional filters.
        
        Args:
            db: Database session
            template_id: Optional template ID filter
            field_name: Optional field name filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of ClauseCache instances
        """
        query = db.query(ClauseCache)
        
        if template_id:
            query = query.filter(ClauseCache.template_id == template_id)
        
        if field_name:
            query = query.filter(ClauseCache.field_name == field_name)
        
        return query.order_by(ClauseCache.last_used_at.desc()).limit(limit).offset(offset).all()
    
    def delete_clause(self, db: Session, clause_id: int) -> bool:
        """
        Delete a cached clause.
        
        Args:
            db: Database session
            clause_id: Clause cache ID
            
        Returns:
            True if deleted, False if not found
        """
        clause = db.query(ClauseCache).filter(ClauseCache.id == clause_id).first()
        if clause:
            db.delete(clause)
            db.commit()
            logger.info(f"Deleted cached clause {clause_id}")
            return True
        return False
