"""
Input validation utilities for DBForged.

Provides sanitization and validation functions for user input.
"""

from __future__ import annotations

import re
from typing import Any, Optional, Union


# Maximum lengths for various inputs
MAX_NAME_LENGTH = 50
MAX_COMMAND_ARG_LENGTH = 200
MAX_QUEST_ID_LENGTH = 64
MAX_GUILD_NAME_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 500
MAX_TECHNIQUE_NAME_LENGTH = 40


# Characters that are dangerous in various contexts
DANGEROUS_CHARS_PATTERN = re.compile(r'[\x00-\x1f\x7f-\x9f]')  # Control chars
EVENNIA_MARKUP_PATTERN = re.compile(r'\|[a-zA-Z0-9]+')


def sanitize_string(value: str, max_length: int = MAX_COMMAND_ARG_LENGTH) -> str:
    """
    Sanitize a string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove control characters
    value = DANGEROUS_CHARS_PATTERN.sub('', value)
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()


def sanitize_name(value: str, max_length: int = MAX_NAME_LENGTH) -> str:
    """
    Sanitize a name input.
    
    Args:
        value: Name string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized name
    """
    if not value:
        return ""
    
    # Remove control characters and dangerous chars
    value = DANGEROUS_CHARS_PATTERN.sub('', value)
    
    # Allow only alphanumeric, spaces, hyphens, underscores
    value = re.sub(r'[^\\w\\s-]', '', value)
    
    # Truncate
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()


def sanitize_quest_id(value: str) -> str:
    """
    Sanitize a quest ID.
    
    Args:
        value: Quest ID string
        
    Returns:
        Sanitized quest ID
    """
    if not value:
        return ""
    
    # Remove control characters
    value = DANGEROUS_CHARS_PATTERN.sub('', value)
    
    # Only allow alphanumeric, underscores, hyphens
    value = re.sub(r'[^\\w-]', '', value)
    
    # Truncate
    if len(value) > MAX_QUEST_ID_LENGTH:
        value = value[:MAX_QUEST_ID_LENGTH]
    
    return value.strip()


def sanitize_guild_name(value: str) -> str:
    """
    Sanitize a guild name.
    
    Args:
        value: Guild name string
        
    Returns:
        Sanitized guild name
    """
    if not value:
        return ""
    
    # Remove control characters
    value = DANGEROUS_CHARS_PATTERN.sub('', value)
    
    # Allow alphanumeric, spaces, hyphens
    value = re.sub(r'[^\\w\\s-]', '', value)
    
    # Truncate
    if len(value) > MAX_GUILD_NAME_LENGTH:
        value = value[:MAX_GUILD_NAME_LENGTH]
    
    return value.strip()


def validate_numeric(value: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """
    Validate and parse a numeric input.
    
    Args:
        value: String to parse as integer
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        
    Returns:
        Parsed integer or None if invalid
    """
    if not value:
        return None
    
    try:
        num = int(value)
        
        if min_val is not None and num < min_val:
            return None
        if max_val is not None and num > max_val:
            return None
            
        return num
    except (ValueError, TypeError):
        return None


def validate_positive_int(value: str) -> Optional[int]:
    """
    Validate a positive integer.
    
    Args:
        value: String to parse
        
    Returns:
        Positive integer or None if invalid
    """
    return validate_numeric(value, min_val=1)


def validate_range(value: str, min_val: int = 0, max_val: int = 100) -> Optional[int]:
    """
    Validate an integer in a range.
    
    Args:
        value: String to parse
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Integer in range or None if invalid
    """
    return validate_numeric(value, min_val=min_val, max_val=max_val)


def strip_evennia_markup(value: str) -> str:
    """
    Strip Evennia markup from a string.
    
    This prevents players from injecting color codes or other
    markup into content that will be displayed to others.
    
    Args:
        value: String with potential markup
        
    Returns:
        String with markup removed
    """
    if not value:
        return ""
    
    # Replace markup with empty string
    return EVENNIA_MARKUP_PATTERN.sub('', value)


def validate_player_name(value: str) -> bool:
    """
    Validate a player name for creation.
    
    Args:
        value: Proposed player name
        
    Returns:
        True if valid
    """
    if not value or len(value) < 2:
        return False
    if len(value) > MAX_NAME_LENGTH:
        return False
    
    # Must be alphanumeric with optional spaces
    return bool(re.match(r'^[\\w\\s]+$', value))


def validate_direction(value: str) -> Optional[str]:
    """
    Validate a direction input.
    
    Args:
        value: Direction string
        
    Returns:
        Normalized direction or None
    """
    if not value:
        return None
    
    value = value.lower().strip()
    
    direction_map = {
        'n': 'north', 'north': 'north',
        's': 'south', 'south': 'south',
        'e': 'east', 'east': 'east',
        'w': 'west', 'west': 'west',
        'ne': 'northeast', 'northeast': 'northeast',
        'nw': 'northwest', 'northwest': 'northwest',
        'se': 'southeast', 'southeast': 'southeast',
        'sw': 'southwest', 'southwest': 'southwest',
        'u': 'up', 'up': 'up',
        'd': 'down', 'down': 'down',
    }
    
    return direction_map.get(value)
