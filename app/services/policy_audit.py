"""
Policy Audit Service for CreditNexus.

Provides centralized logging and querying of policy decisions for audit trail
and compliance reporting.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.db.models import PolicyDecision as PolicyDecisionModel
from app.services.policy_service import PolicyDecision

logger = logging.getLogger(__name__)


def log_policy_decision(
    db: Session,
    policy_decision: PolicyDecision,
    transaction_id: str,
    transaction_type: str,
    cdm_events: Optional[List[Dict[str, Any]]] = None,
    document_id: Optional[int] = None,
    loan_asset_id: Optional[int] = None,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> PolicyDecisionModel:
    """
    Log a policy decision to the audit trail.
    
    Args:
        db: Database session
        policy_decision: PolicyDecision dataclass from policy service
        transaction_id: Transaction identifier
        transaction_type: Type of transaction
        cdm_events: Optional list of CDM events (PolicyEvaluation events)
        document_id: Optional document ID
        loan_asset_id: Optional loan asset ID
        user_id: Optional user ID
        metadata: Optional additional metadata
        
    Returns:
        Created PolicyDecisionModel instance
    """
    try:
        # Merge metadata
        decision_metadata = metadata or {}
        decision_metadata.update(policy_decision.metadata)
        
        policy_decision_db = PolicyDecisionModel(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            decision=policy_decision.decision,
            rule_applied=policy_decision.rule_applied,
            trace_id=policy_decision.trace_id,
            trace=policy_decision.trace,
            matched_rules=policy_decision.matched_rules,
            metadata=decision_metadata,
            cdm_events=cdm_events or [],
            document_id=document_id,
            loan_asset_id=loan_asset_id,
            user_id=user_id
        )
        
        db.add(policy_decision_db)
        db.commit()
        db.refresh(policy_decision_db)
        
        logger.info(
            f"Policy decision logged: transaction_id={transaction_id}, "
            f"decision={policy_decision.decision}, rule={policy_decision.rule_applied}"
        )
        
        return policy_decision_db
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to log policy decision: {e}", exc_info=True)
        raise


def get_policy_decisions(
    db: Session,
    transaction_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    decision: Optional[str] = None,
    rule_applied: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[PolicyDecisionModel]:
    """
    Query policy decisions with filtering.
    
    Args:
        db: Database session
        transaction_id: Filter by transaction ID
        transaction_type: Filter by transaction type
        decision: Filter by decision (ALLOW, BLOCK, FLAG)
        rule_applied: Filter by rule name
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of PolicyDecisionModel instances
    """
    try:
        query = db.query(PolicyDecisionModel)
        
        # Apply filters
        if transaction_id:
            query = query.filter(PolicyDecisionModel.transaction_id == transaction_id)
        
        if transaction_type:
            query = query.filter(PolicyDecisionModel.transaction_type == transaction_type)
        
        if decision:
            query = query.filter(PolicyDecisionModel.decision == decision.upper())
        
        if rule_applied:
            query = query.filter(PolicyDecisionModel.rule_applied == rule_applied)
        
        if start_date:
            query = query.filter(PolicyDecisionModel.created_at >= start_date)
        
        if end_date:
            query = query.filter(PolicyDecisionModel.created_at <= end_date)
        
        # Order by created_at descending
        query = query.order_by(PolicyDecisionModel.created_at.desc())
        
        # Apply pagination
        decisions = query.offset(offset).limit(limit).all()
        
        return decisions
        
    except Exception as e:
        logger.error(f"Failed to query policy decisions: {e}", exc_info=True)
        raise


def get_policy_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    transaction_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get aggregated policy decision statistics.
    
    Args:
        db: Database session
        start_date: Filter by start date
        end_date: Filter by end date
        transaction_type: Filter by transaction type
        
    Returns:
        Dictionary with statistics:
        - total_processed: Total number of decisions
        - decisions: Count by decision type (ALLOW, BLOCK, FLAG)
        - rules: Count by rule_applied
        - transaction_types: Count by transaction_type
        - time_series: Daily counts for charting
    """
    try:
        query = db.query(PolicyDecisionModel)
        
        # Apply filters
        if start_date:
            query = query.filter(PolicyDecisionModel.created_at >= start_date)
        
        if end_date:
            query = query.filter(PolicyDecisionModel.created_at <= end_date)
        
        if transaction_type:
            query = query.filter(PolicyDecisionModel.transaction_type == transaction_type)
        
        # Total count
        total_processed = query.count()
        
        # Count by decision
        decisions_query = query.with_entities(
            PolicyDecisionModel.decision,
            func.count(PolicyDecisionModel.id).label('count')
        ).group_by(PolicyDecisionModel.decision)
        
        decisions = {
            "ALLOW": 0,
            "BLOCK": 0,
            "FLAG": 0
        }
        
        for decision, count in decisions_query.all():
            decisions[decision] = count
        
        # Count by rule_applied
        rules_query = query.filter(
            PolicyDecisionModel.rule_applied.isnot(None)
        ).with_entities(
            PolicyDecisionModel.rule_applied,
            func.count(PolicyDecisionModel.id).label('count')
        ).group_by(PolicyDecisionModel.rule_applied).order_by(
            func.count(PolicyDecisionModel.id).desc()
        ).limit(10)  # Top 10 rules
        
        rules = [
            {"rule": rule, "count": count}
            for rule, count in rules_query.all()
        ]
        
        # Count by transaction_type
        types_query = query.with_entities(
            PolicyDecisionModel.transaction_type,
            func.count(PolicyDecisionModel.id).label('count')
        ).group_by(PolicyDecisionModel.transaction_type)
        
        transaction_types = {
            transaction_type: count
            for transaction_type, count in types_query.all()
        }
        
        # Time series data (daily counts)
        if start_date and end_date:
            time_series = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                
                day_count = query.filter(
                    and_(
                        PolicyDecisionModel.created_at >= day_start,
                        PolicyDecisionModel.created_at <= day_end
                    )
                ).count()
                
                time_series.append({
                    "date": current_date.isoformat(),
                    "count": day_count
                })
                
                current_date += timedelta(days=1)
        else:
            # Default to last 30 days
            default_end = datetime.utcnow()
            default_start = default_end - timedelta(days=30)
            
            time_series = []
            current_date = default_start.date()
            end_date_only = default_end.date()
            
            while current_date <= end_date_only:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                
                day_count = db.query(PolicyDecisionModel).filter(
                    and_(
                        PolicyDecisionModel.created_at >= day_start,
                        PolicyDecisionModel.created_at <= day_end
                    )
                ).count()
                
                time_series.append({
                    "date": current_date.isoformat(),
                    "count": day_count
                })
                
                current_date += timedelta(days=1)
        
        return {
            "total_processed": total_processed,
            "decisions": decisions,
            "rules": rules,
            "transaction_types": transaction_types,
            "time_series": time_series
        }
        
    except Exception as e:
        logger.error(f"Failed to get policy statistics: {e}", exc_info=True)
        raise



