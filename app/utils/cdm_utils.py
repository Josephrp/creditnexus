"""Utility functions for CDM data manipulation.

This module provides helper functions for working with nested CDM data structures,
including getting, setting, and removing nested fields using dot notation paths.
"""

from typing import Any, Dict


def get_nested_value(cdm_data: Dict[str, Any], field_path: str) -> Any:
    """Get value from nested CDM structure using dot notation.
    
    Supports array indices in the path (e.g., "parties[0].name").
    
    Args:
        cdm_data: The CDM data dictionary
        field_path: Dot-notation path to the field (e.g., "parties[0].name", "facilities[1].commitment_amount.amount")
        
    Returns:
        The value at the specified path, or None if not found
    """
    keys = field_path.split('.')
    current = cdm_data
    
    for key in keys:
        if current is None or not isinstance(current, dict):
            return None
            
        # Handle array indices like "parties[0]"
        import re
        match = re.match(r'^(\w+)\[(\d+)\]$', key)
        if match:
                array_key, index = match.groups()
                if array_key not in current or not isinstance(current[array_key], list):
                    return None
                try:
                    current = current[array_key][int(index)]
                except (IndexError, ValueError):
                    return None
        else:
            current = current.get(key)
            if current is None:
                return None
    
    return current


def set_nested_value(cdm_data: Dict[str, Any], field_path: str, value: Any) -> Dict[str, Any]:
    """Set value in nested CDM structure, preserving all other fields.
    
    Supports array indices in the path (e.g., "parties[0].name").
    
    Args:
        cdm_data: The CDM data dictionary
        field_path: Dot-notation path to the field
        value: The new value to set
        
    Returns:
        A new dictionary with the updated value (deep copy)
    """
    import json
    import re
    
    # Deep clone the data
    result = json.loads(json.dumps(cdm_data))
    keys = field_path.split('.')
    current = result
    
    # Navigate to the parent of the target field
    for i, key in enumerate(keys[:-1]):
        # Handle array indices
        array_match = re.match(r'^(\w+)\[(\d+)\]$', key)
        if array_match:
            array_key, index = array_match.groups()
            if array_key not in current:
                current[array_key] = []
            if not isinstance(current[array_key], list):
                current[array_key] = []
            # Ensure list is long enough
            while len(current[array_key]) <= int(index):
                current[array_key].append({})
            if not isinstance(current[array_key][int(index)], dict):
                current[array_key][int(index)] = {}
            current = current[array_key][int(index)]
        else:
            if key not in current:
                current[key] = {}
            if not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
    
    # Set the final value
    last_key = keys[-1]
    array_match = re.match(r'^(\w+)\[(\d+)\]$', last_key)
    if array_match:
        array_key, index = array_match.groups()
        if array_key not in current:
            current[array_key] = []
        while len(current[array_key]) <= int(index):
            current[array_key].append(None)
        current[array_key][int(index)] = value
    else:
        current[last_key] = value
    
    return result


def remove_nested_field(cdm_data: Dict[str, Any], field_path: str) -> Dict[str, Any]:
    """Remove field from nested structure safely.
    
    Args:
        cdm_data: The CDM data dictionary
        field_path: Dot-notation path to the field to remove
        
    Returns:
        A new dictionary with the field removed (deep copy)
    """
    import json
    import re
    
    # Deep clone the data
    result = json.loads(json.dumps(cdm_data))
    keys = field_path.split('.')
    current = result
    
    # Navigate to the parent of the target field
    for i, key in enumerate(keys[:-1]):
        if current is None or not isinstance(current, dict):
            return result  # Path doesn't exist, return original
            
        array_match = re.match(r'^(\w+)\[(\d+)\]$', key)
        if array_match:
            array_key, index = array_match.groups()
            if array_key not in current or not isinstance(current[array_key], list):
                return result  # Path doesn't exist
            try:
                current = current[array_key][int(index)]
            except (IndexError, ValueError):
                return result  # Path doesn't exist
        else:
            current = current.get(key)
            if current is None or not isinstance(current, dict):
                return result  # Path doesn't exist
    
    # Remove the final field
    if current is None or not isinstance(current, dict):
        return result
        
    last_key = keys[-1]
    array_match = re.match(r'^(\w+)\[(\d+)\]$', last_key)
    if array_match:
        array_key, index = array_match.groups()
        if array_key in current and isinstance(current[array_key], list):
            try:
                del current[array_key][int(index)]
            except (IndexError, ValueError):
                pass
    else:
        if last_key in current:
            del current[last_key]
    
    return result
