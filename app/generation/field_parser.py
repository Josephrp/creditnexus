"""
CDM field path parser for navigating nested CreditAgreement structures.

Supports paths like:
- "parties[role='Borrower'].name"
- "facilities[0].commitment_amount.amount"
- "agreement_date"
- "governing_law"
"""

import re
import logging
from typing import List, Any, Optional, Dict, Union

logger = logging.getLogger(__name__)


class FieldPathParser:
    """
    Parser for CDM field paths to extract values from nested structures.
    
    Supports:
    - Simple attribute access: "agreement_date"
    - Nested attributes: "facilities[0].commitment_amount.amount"
    - List filtering: "parties[role='Borrower'].name"
    - Array indexing: "facilities[0]"
    """
    
    # Pattern for list filters: parties[role='Borrower']
    LIST_FILTER_PATTERN = re.compile(r'^(\w+)\[(\w+)=[\'"]?([^\'"]+)[\'"]?\]$')
    
    # Pattern for array index: facilities[0]
    ARRAY_INDEX_PATTERN = re.compile(r'^(\w+)\[(\d+)\]$')
    
    @staticmethod
    def parse_field_path(path: str) -> List[Union[str, Dict[str, Any]]]:
        """
        Parse a field path into segments.
        
        Args:
            path: Field path (e.g., "parties[role='Borrower'].name")
            
        Returns:
            List of path segments, where each segment is either:
            - A string (attribute name)
            - A dict with 'filter' key (list filter: {"filter": {"role": "Borrower"}})
            - A dict with 'index' key (array index: {"index": 0})
            
        Example:
            "parties[role='Borrower'].name" -> [
                {"filter": {"role": "Borrower"}},
                "name"
            ]
            "facilities[0].commitment_amount.amount" -> [
                {"index": 0},
                "commitment_amount",
                "amount"
            ]
        """
        segments = []
        current_segment = ""
        i = 0
        
        while i < len(path):
            char = path[i]
            
            if char == '.':
                # End of current segment
                if current_segment:
                    segments.append(current_segment)
                    current_segment = ""
            elif char == '[':
                # Start of filter or index
                # Preserve attribute name before bracket for pattern matching
                attr_name_before_bracket = current_segment if current_segment else None
                # Don't add to segments yet - we'll add it after parsing the bracket
                current_segment = ""
                
                # Find matching closing bracket
                bracket_content = ""
                bracket_depth = 1
                i += 1
                while i < len(path) and bracket_depth > 0:
                    if path[i] == '[':
                        bracket_depth += 1
                    elif path[i] == ']':
                        bracket_depth -= 1
                        if bracket_depth > 0:
                            bracket_content += path[i]
                    else:
                        bracket_content += path[i]
                    i += 1
                
                # Parse bracket content
                # Reconstruct full segment for pattern matching using preserved attribute name
                full_segment = (attr_name_before_bracket + "[" + bracket_content + "]") if attr_name_before_bracket else ("[" + bracket_content + "]")
                filter_match = FieldPathParser.LIST_FILTER_PATTERN.match(full_segment)
                index_match = FieldPathParser.ARRAY_INDEX_PATTERN.match(full_segment)
                
                if filter_match:
                    # List filter: parties[role='Borrower']
                    attr_name = filter_match.group(1)
                    filter_key = filter_match.group(2)
                    filter_value = filter_match.group(3)
                    # Add attribute name, then filter
                    segments.append(attr_name)
                    segments.append({"filter": {filter_key: filter_value}})
                elif index_match:
                    # Array index: facilities[0]
                    attr_name = index_match.group(1)
                    index = int(index_match.group(2))
                    # Add attribute name, then index
                    segments.append(attr_name)
                    segments.append({"index": index})
                else:
                    # Try to parse as simple index
                    try:
                        index = int(bracket_content)
                        attr_name = attr_name_before_bracket if attr_name_before_bracket else (segments[-1] if segments else None)
                        if attr_name:
                            segments.append(attr_name)
                        segments.append({"index": index})
                    except ValueError:
                        logger.warning(f"Could not parse bracket content: {bracket_content} in path: {path}")
                
                current_segment = ""
                continue
            else:
                current_segment += char
            
            i += 1
        
        # Add remaining segment
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    @staticmethod
    def get_nested_value(obj: Any, path: str) -> Optional[Any]:
        """
        Get value from nested object using field path.
        
        Args:
            obj: Root object (e.g., CreditAgreement instance)
            path: Field path (e.g., "parties[role='Borrower'].name")
            
        Returns:
            Value at path or None if not found
            
        Example:
            agreement = CreditAgreement(...)
            borrower_name = FieldPathParser.get_nested_value(
                agreement, 
                "parties[role='Borrower'].name"
            )
        """
        if not obj or not path:
            return None
        
        segments = FieldPathParser.parse_field_path(path)
        
        current = obj
        
        for segment in segments:
            if current is None:
                return None
            
            if isinstance(segment, dict):
                if "filter" in segment:
                    # List filter: find item matching filter criteria
                    filter_dict = segment["filter"]
                    if isinstance(current, list):
                        # Find first item matching all filter criteria
                        for item in current:
                            if isinstance(item, dict):
                                match = all(
                                    str(getattr(item, key, None)).lower() == str(value).lower()
                                    for key, value in filter_dict.items()
                                )
                            else:
                                # Pydantic model
                                match = all(
                                    str(getattr(item, key, None)).lower() == str(value).lower()
                                    for key, value in filter_dict.items()
                                )
                            if match:
                                current = item
                                break
                        else:
                            return None  # No match found
                    else:
                        return None
                elif "index" in segment:
                    # Array index
                    index = segment["index"]
                    if isinstance(current, list) and 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
            else:
                # Attribute access
                if isinstance(current, dict):
                    current = current.get(segment)
                else:
                    current = getattr(current, segment, None)
        
        return current
    
    @staticmethod
    def set_nested_value(obj: Any, path: str, value: Any) -> None:
        """
        Set value in nested object using field path.
        
        Args:
            obj: Root object (e.g., CreditAgreement instance or dict)
            path: Field path (e.g., "parties[role='Borrower'].name")
            value: Value to set
            
        Note:
            This creates intermediate objects if they don't exist.
            For Pydantic models, this may not work directly - use model_copy() instead.
        """
        if not obj or not path:
            return
        
        segments = FieldPathParser.parse_field_path(path)
        current = obj
        
        # Navigate to parent of target
        for i, segment in enumerate(segments[:-1]):
            next_segment = segments[i + 1]
            
            if isinstance(segment, dict):
                if "filter" in segment:
                    # List filter - find matching item in list
                    filter_dict = segment["filter"]
                    if isinstance(current, list):
                        found_item = None
                        for idx, item in enumerate(current):
                            if isinstance(item, dict):
                                match = all(
                                    str(item.get(key)).lower() == str(value).lower()
                                    for key, value in filter_dict.items()
                                )
                            else:
                                match = all(
                                    str(getattr(item, key, None)).lower() == str(value).lower()
                                    for key, value in filter_dict.items()
                                )
                            if match:
                                found_item = item
                                # Store reference to the list and index for later modification
                                # We need to track this so we can update the item in place
                                if not hasattr(obj, '_field_parser_context'):
                                    obj._field_parser_context = {}
                                obj._field_parser_context['current_list'] = current
                                obj._field_parser_context['current_index'] = idx
                                current = item
                                break
                        if found_item is None:
                            # Item not found - create new one if we're at the end
                            if i == len(segments) - 2:  # Last segment before final
                                new_item = filter_dict.copy()  # Start with filter criteria
                                current.append(new_item)
                                current = new_item
                                if not hasattr(obj, '_field_parser_context'):
                                    obj._field_parser_context = {}
                                obj._field_parser_context['current_list'] = current
                                obj._field_parser_context['current_index'] = len(current) - 1
                elif "index" in segment:
                    # Array index
                    index = segment["index"]
                    if isinstance(current, list) and 0 <= index < len(current):
                        current = current[index]
            else:
                # Attribute access
                if isinstance(current, dict):
                    if segment not in current:
                        # Create intermediate dict
                        if isinstance(next_segment, dict) and "index" in next_segment:
                            current[segment] = []
                        else:
                            current[segment] = {}
                    current = current[segment]
                else:
                    current = getattr(current, segment, None)
        
        # Set final value
        final_segment = segments[-1]
        if isinstance(final_segment, str):
            if isinstance(current, dict):
                # If setting a nested object/dict and value is also a dict, merge instead of replace
                # This preserves existing fields in the object
                if isinstance(value, dict) and final_segment in current and isinstance(current[final_segment], dict):
                    # Merge dictionaries to preserve existing fields
                    current[final_segment].update(value)
                else:
                    # Simple field assignment
                    current[final_segment] = value
            else:
                setattr(current, final_segment, value)
    
    @staticmethod
    def _extract_list_filter(segment: str) -> Optional[Dict[str, str]]:
        """
        Extract list filter from segment string.
        
        Args:
            segment: Segment like "parties[role='Borrower']"
            
        Returns:
            Dict with filter criteria or None
        """
        match = FieldPathParser.LIST_FILTER_PATTERN.match(segment)
        if match:
            return {match.group(2): match.group(3)}
        return None
    
    @staticmethod
    def _filter_list(items: List[Any], filter_dict: Dict[str, str]) -> Optional[Any]:
        """
        Filter list to find first item matching criteria.
        
        Args:
            items: List of items to filter
            filter_dict: Filter criteria (e.g., {"role": "Borrower"})
            
        Returns:
            First matching item or None
        """
        if not items:
            return None
        
        for item in items:
            if isinstance(item, dict):
                match = all(
                    str(item.get(key)).lower() == str(value).lower()
                    for key, value in filter_dict.items()
                )
            else:
                # Pydantic model or object
                match = all(
                    str(getattr(item, key, None)).lower() == str(value).lower()
                    for key, value in filter_dict.items()
                )
            if match:
                return item
        
        return None
















