"""
CDM State-Transition Logic for Policy Decisions.

This module implements CDM-compliant state machine for policy decisions,
following the CDM principle: "Fully functional event model with state-transition logic".
"""

from enum import Enum
from typing import Dict, Any, Optional


class PolicyDecisionState(str, Enum):
    """CDM-compliant state enumeration for policy decisions."""
    PENDING = "PENDING"
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    FLAGGED = "FLAGGED"


class CDMPolicyStateMachine:
    """
    CDM state-transition logic for policy decisions.
    
    Follows CDM principle: "Fully functional event model with state-transition logic"
    """
    
    TRANSITIONS: Dict[PolicyDecisionState, list] = {
        PolicyDecisionState.PENDING: [
            PolicyDecisionState.ALLOWED,
            PolicyDecisionState.BLOCKED,
            PolicyDecisionState.FLAGGED
        ],
        PolicyDecisionState.FLAGGED: [
            PolicyDecisionState.ALLOWED,
            PolicyDecisionState.BLOCKED
        ],  # Can be reviewed and resolved
        PolicyDecisionState.ALLOWED: [],  # Terminal state
        PolicyDecisionState.BLOCKED: [],  # Terminal state
    }
    
    @classmethod
    def can_transition(
        cls,
        from_state: PolicyDecisionState,
        to_state: PolicyDecisionState
    ) -> bool:
        """
        Check if state transition is valid (CDM validation).
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is valid, False otherwise
        """
        return to_state in cls.TRANSITIONS.get(from_state, [])
    
    @classmethod
    def apply_decision(
        cls,
        current_state: PolicyDecisionState,
        decision: str  # "ALLOW", "BLOCK", "FLAG"
    ) -> PolicyDecisionState:
        """
        Apply policy decision with state-transition validation.
        
        CDM Process: Validation → State Transition → Event Creation
        
        Args:
            current_state: Current policy decision state
            decision: Policy decision string ("ALLOW", "BLOCK", "FLAG")
            
        Returns:
            New state after applying decision
            
        Raises:
            ValueError: If decision is invalid or transition is not allowed
        """
        # Map decision to state
        decision_state_map = {
            "ALLOW": PolicyDecisionState.ALLOWED,
            "BLOCK": PolicyDecisionState.BLOCKED,
            "FLAG": PolicyDecisionState.FLAGGED
        }
        
        target_state = decision_state_map.get(decision.upper())
        if not target_state:
            raise ValueError(f"Invalid decision: {decision}. Must be one of: ALLOW, BLOCK, FLAG")
        
        # Validate transition (CDM validation)
        if not cls.can_transition(current_state, target_state):
            raise ValueError(
                f"Invalid state transition: {current_state} → {target_state}. "
                f"Valid transitions from {current_state}: {cls.TRANSITIONS.get(current_state, [])}"
            )
        
        return target_state
    
    @classmethod
    def get_valid_transitions(cls, current_state: PolicyDecisionState) -> list:
        """
        Get list of valid transitions from current state.
        
        Args:
            current_state: Current policy decision state
            
        Returns:
            List of valid target states
        """
        return cls.TRANSITIONS.get(current_state, [])














