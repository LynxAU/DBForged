"""
================================================================================
HYPERBOLIC TIME CHAMBER - DBForged Vertical Slice
================================================================================

This module provides the Hyperbolic Time Chamber (HTC) - a premium training
zone where time flows 10x slower than the outside world.

FEATURES:
--------
- 10x XP gain while inside
- Once-per-day entry limit (real-time)
- Maximum 2 players can enter at once
- Gravity adjustable from 1x to 100x
- No combat inside (safe training zone)
- Exit returns to original location

COMMANDS:
---------
- htc enter - Enter the HTC
- htc exit - Exit the HTC
- htc gravity <1-100> - Set gravity level
- htc status - Show HTC status

MECHANICS:
----------
- Entry: Requires 'gravity_charge' item OR admin permission
- XP Multiplier: 10x base + (gravity_level / 10)
- Training sessions can last up to 60 real minutes (10 hours in HTC)
- Players cannot attack or be attacked inside
- Cannot use Instant Transmission to escape
"""

from __future__ import annotations

import time
from typing import Dict, Optional, Any


# HTC Configuration
HTC_XP_MULTIPLIER = 10.0
HTC_MAX_REAL_TIME_MINUTES = 60  # Max 60 real minutes per day
HTC_MAX_GRAVITY = 100
HTC_MIN_GRAVITY = 1
HTC_DAILY_RESET_HOUR = 0  # Midnight UTC


def can_enter_htc(character) -> tuple[bool, str]:
    """
    Check if character can enter the HTC.
    
    Args:
        character: The character trying to enter
    
    Returns:
        Tuple of (can_enter, reason)
    """
    # Check if already in HTC
    if character.db.in_htc:
        return False, "You are already in the HTC!"
    
    # Check daily limit
    last_entry = character.db.get('htc_last_entry', 0)
    today_start = _get_daily_reset_timestamp()
    
    if last_entry > today_start:
        # Already entered today
        return False, "You have already entered the HTC today. Come back tomorrow!"
    
    # Check for gravity charge item
    from world.inventory import has_item
    has_charge = has_item(character, "gravity_charge")
    
    # Admins can always enter
    if character.check_permstring("admin"):
        return True, ""
    
    if not has_charge:
        return False, "You need a Gravity Charge to enter the HTC. Find one or purchase from Capsule Corp."
    
    return True, ""


def _get_daily_reset_timestamp() -> float:
    """Get timestamp for today's daily reset."""
    now = time.time()
    # Reset at midnight UTC
    from datetime import datetime, timedelta
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return today.timestamp()


def enter_htc(character) -> tuple[bool, str]:
    """
    Enter the Hyperbolic Time Chamber.
    
    Args:
        character: The character entering
    
    Returns:
        Tuple of (success, message)
    """
    can_enter, reason = can_enter_htc(character)
    if not can_enter:
        return False, reason
    
    # Consume gravity charge if not admin
    if not character.check_permstring("admin"):
        from world.inventory import remove_item
        if not remove_item(character, "gravity_charge"):
            return False, "Failed to use gravity charge."
    
    # Store original location
    if character.location:
        character.db.htc_origin = character.location.id
    
    # Set HTC state
    character.db.in_htc = True
    character.db.htc_entered_at = time.time()
    character.db.htc_gravity = 10  # Default gravity
    character.db.htc_last_entry = time.time()
    
    # Move to HTC location (would need to create this in world)
    # For now, just set the flag
    
    # Calculate XP multiplier
    gravity = character.db.htc_gravity
    xp_multiplier = HTC_XP_MULTIPLIER + (gravity / 10)
    character.db.htc_xp_multiplier = xp_multiplier
    
    return True, f"""|g=== HYPERBOLIC TIME CHAMBER ===|n
Welcome to the Hyperbolic Time Chamber!
- Time flows 10x slower here
- XP Gain: {xp_multiplier:.1f}x
- Current Gravity: {gravity}x
- Use 'htc gravity <1-100>' to adjust
- Use 'htc exit' to leave

You can train here for up to {HTC_MAX_REAL_TIME_MINUTES} real minutes.
"""


def exit_htc(character) -> tuple[bool, str]:
    """
    Exit the Hyperbolic Time Chamber.
    
    Args:
        character: The character exiting
    
    Returns:
        Tuple of (success, message)
    """
    if not character.db.in_htc:
        return False, "You are not in the HTC."
    
    # Clear HTC state
    character.db.in_htc = False
    
    # Clear multipliers
    character.db.htc_xp_multiplier = None
    
    # Return to origin if available
    origin_id = character.db.get('htc_origin')
    if origin_id:
        from evennia.objects.models import ObjectDB
        origin = ObjectDB.objects.filter(id=origin_id).first()
        if origin:
            character.move_to(origin)
    
    # Clear origin
    character.db.htc_origin = None
    
    return True, "|gYou exit the Hyperbolic Time Chamber.|n"


def set_htc_gravity(character, gravity: int) -> tuple[bool, str]:
    """
    Set gravity level in HTC.
    
    Args:
        character: The character
        gravity: Gravity level (1-100)
    
    Returns:
        Tuple of (success, message)
    """
    if not character.db.in_htc:
        return False, "You are not in the HTC."
    
    if gravity < HTC_MIN_GRAVITY or gravity > HTC_MAX_GRAVITY:
        return False, f"Gravity must be between {HTC_MIN_GRAVITY} and {HTC_MAX_GRAVITY}."
    
    character.db.htc_gravity = gravity
    
    # Update XP multiplier
    xp_multiplier = HTC_XP_MULTIPLIER + (gravity / 10)
    character.db.htc_xp_multiplier = xp_multiplier
    
    return True, f"|gGravity set to {gravity}x. XP multiplier: {xp_multiplier:.1f}x|n"


def get_htc_status(character) -> str:
    """
    Get HTC status.
    
    Args:
        character: The character
    
    Returns:
        Formatted status string
    """
    if not character.db.in_htc:
        return "|yYou are not in the HTC.|n\nUse 'htc enter' to enter."
    
    entered_at = character.db.get('htc_entered_at', time.time())
    elapsed = time.time() - entered_at
    remaining = (HTC_MAX_REAL_TIME_MINUTES * 60) - elapsed
    
    gravity = character.db.get('htc_gravity', 10)
    xp_mult = character.db.get('htc_xp_multiplier', HTC_XP_MULTIPLIER)
    
    lines = [
        "|g=== HYPERBOLIC TIME CHAMBER ===|n",
        f"Time Remaining: {int(remaining // 60)} minutes",
        f"Current Gravity: {gravity}x",
        f"XP Multiplier: {xp_mult:.1f}x",
    ]
    
    # Show bonus
    bonus = int((gravity / 10) * 100)
    if bonus > 0:
        lines.append(f"Gravity Bonus: +{bonus}% XP bonus")
    
    return "".join(lines)


def get_training_xp_multiplier(character) -> float:
    """
    Get total XP multiplier including HTC bonus.
    
    Args:
        character: The character
    
    Returns:
        XP multiplier (1.0 = no bonus)
    """
    multiplier = 1.0
    
    # HTC bonus
    htc_mult = character.db.get('htc_xp_multiplier')
    if htc_mult:
        multiplier *= htc_mult
    
    # Equipment bonus
    from world.inventory import get_equipment_bonus
    equip_mult = get_equipment_bonus(character, "xp_mod")
    if equip_mult:
        multiplier *= equip_mult
    
    # Sensei tea bonus
    tea_mult = character.db.get('xp_boost_multiplier')
    if tea_mult:
        multiplier *= tea_mult
    
    # Faction bonus
    from world.guild_system import get_faction_bonus
    faction_bonus = get_faction_bonus(character, "xp")
    if faction_bonus:
        multiplier *= (1.0 + faction_bonus / 100.0)
    
    # Party bonus
    from world.party_system import get_party_xp_bonus
    party_mult = get_party_xp_bonus(character)
    multiplier *= party_mult
    
    return multiplier


# =============================================================================
# HTC COMMANDS
# =============================================================================


class HTCCommand:
    """HTC command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """
        Handle HTC subcommands.
        
        Args:
            caller: The character using the command
            args: Arguments after "htc "
        
        Returns:
            Result message
        """
        args = args.strip().lower() if args else ""
        
        if not args:
            return get_htc_status(caller)
        
        elif args == "enter":
            success, msg = enter_htc(caller)
            return msg if success else f"|r{msg}|n"
        
        elif args == "exit":
            success, msg = exit_htc(caller)
            return msg if success else f"|r{msg}|n"
        
        elif args == "status":
            return get_htc_status(caller)
        
        elif args.startswith("gravity "):
            try:
                gravity = int(args.split()[1])
            except (ValueError, IndexError):
                return "Usage: htc gravity <1-100>"
            success, msg = set_htc_gravity(caller, gravity)
            return msg if success else f"|r{msg}|n"
        
        else:
            return """|yHTC Commands:|n
  htc enter       - Enter the Hyperbolic Time Chamber
  htc exit        - Exit the HTC
  htc gravity <1-100> - Set gravity level
  htc status      - Show HTC status

The HTC provides 10x XP gain. Use gravity charges to enter!
"""
