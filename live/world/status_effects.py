"""
================================================================================
STATUS EFFECTS SYSTEM - DBForged Vertical Slice
================================================================================

This module provides a comprehensive status effect system for DBZ-themed combat.
Status effects can be applied by techniques, environmental factors, or abilities.

STATUS EFFECT CATEGORIES:
-------------------------
DEBUFFS (harmful effects applied by attackers):
  - stun: Cannot act for duration. 2-5 seconds typical.
  - paralysis: Cannot move or attack. 3-8 seconds typical.
  - poison: Takes damage each tick. 10-30 damage/tick, 10-30 seconds.
  - blind: Accuracy reduced by 50%. 5-15 seconds typical.
  - silence: Cannot use ki techniques. 5-20 seconds typical.
  - slow: Speed reduced by 50%. 5-15 seconds typical.
  - weakened: Damage output reduced by 30%. 10-30 seconds typical.
  - rooted: Cannot teleport or move. 3-10 seconds typical.
  - bleeding: Continuous damage that increases over time.

BUFFS (beneficial effects applied self or by allies):
  - regen: Heals HP each tick. 5-20 HP/tick.
  - haste: Speed increased by 50%, cooldowns reduced by 25%.
  - shield: Absorbs incoming damage. Can be physical or ki.
  - reflect: Returns 30-50% of ki damage to attacker.
  - invisibility: Cannot be sensed or targeted (until attacking).
  - ki_boost: Ki attacks deal 30-50% more damage.
  - strength_boost: Melee attacks deal 30-50% more damage.
  - endure: Reduces all incoming damage by 30-50%.
  - critical_boost: Critical hit chance increased by 25%.

TECHNIQUE INTEGRATION:
----------------------
Techniques can apply status effects via their effect_data:
  
  effect_data = {
      "status": "poison",
      "duration": 15,
      "tick_rate": 3,
      "damage_per_tick": 25,
      "sources": ["melee", "ki"]  # what attack types can apply this
  }

COMBAT INTEGRATION:
-------------------
The status_effects_tick() function should be called by the combat handler
every second. This processes:
  - Tick-based effects (poison damage, regen healing)
  - Duration countdown
  - Expiration handling

CHECKING STATUS IN COMBAT:
--------------------------
Before a character acts, check:
  - has_status(char, "stun") -> cannot use actions
  - has_status(char, "paralysis") -> cannot move or attack
  - has_status(char, "blind") -> 50% miss chance
  - has_status(char, "silence") -> cannot use ki techniques

MODIFIER APPLICATION:
---------------------
When calculating damage or stats:
  - get_status_modifier(char, "damage_out") -> multiplies outgoing damage
  - get_status_modifier(char, "damage_in") -> multiplies incoming damage
  - get_status_modifier(char, "speed") -> action speed multiplier
  - get_status_modifier(char, "accuracy") -> hit chance modifier

EXAMPLES:
---------
1. Applying poison to a target:
   apply_status(target, "poison", duration=20, tick_rate=3, 
                damage_per_tick=30, attacker=attacker)

2. Using a healing technique with regen:
   apply_status(caster, "regen", duration=30, tick_rate=5,
                heal_per_tick=50)

3. Checking if opponent can act:
   if has_status(opponent, "stun"):
       attacker.msg("They are stunned and cannot act!")
       return

4. Getting damage modifier with debuffs:
   final_damage = base_damage * get_status_modifier(target, "damage_in")
"""

from __future__ import annotations

import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Status effect types
class StatusType(Enum):
    """Category of status effect."""
    DEBUFF = "debuff"      # Harmful effect
    BUFF = "buff"          # Beneficial effect
    NEUTRAL = "neutral"   # Neither harmful nor beneficial


class StatusFlag(Enum):
    """Special flags for status effects."""
    STUN = "stun"                 # Cannot act
    PARALYSIS = "paralysis"       # Cannot move or attack
    BLIND = "blind"               # Accuracy reduced
    SILENCE = "silence"           # Cannot use ki techniques
    SLOW = "slow"                 # Speed reduced
    ROOTED = "rooted"             # Cannot teleport/move
    INVULNERABLE = "invulnerable" # Cannot be targeted
    INVISIBLE = "invisible"       # Cannot be sensed
    REGEN = "regen"               # Healing over time
    REFLECT = "reflect"           # Reflects damage


# Status effect definitions - configuration for each effect type
STATUS_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # ==================== DEBUFFS ====================
    "stun": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.STUN],
        "default_duration": 3,
        "default_tick_rate": 0,  # No tick damage
        "can_stack": False,
        "max_stacks": 1,
        "description": "Cannot act for duration",
        "combat_penalty": 100,  # 100% penalty = no actions
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 0.0,
    },
    "paralysis": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.PARALYSIS, StatusFlag.ROOTED],
        "default_duration": 5,
        "default_tick_rate": 0,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Cannot move or attack",
        "combat_penalty": 100,
        "damage_mod_out": 0.0,
        "damage_mod_in": 1.0,
        "speed_mod": 0.0,
    },
    "poison": {
        "type": StatusType.DEBUFF,
        "flags": [],
        "default_duration": 15,
        "default_tick_rate": 3,
        "damage_per_tick": 20,
        "can_stack": True,
        "max_stacks": 3,
        "description": "Takes damage each tick",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "bleeding": {
        "type": StatusType.DEBUFF,
        "flags": [],
        "default_duration": 20,
        "default_tick_rate": 2,
        "damage_per_tick": 15,  # Increases with stacks
        "can_stack": True,
        "max_stacks": 5,
        "description": "Continuous damage that increases over time",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "blind": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.BLIND],
        "default_duration": 10,
        "default_tick_rate": 0,
        "accuracy_penalty": 50,  # -50% accuracy
        "can_stack": False,
        "max_stacks": 1,
        "description": "Accuracy reduced by 50%",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "silence": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.SILENCE],
        "default_duration": 10,
        "default_tick_rate": 0,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Cannot use ki techniques",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,  # Can still melee
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "slow": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.SLOW],
        "default_duration": 10,
        "default_tick_rate": 0,
        "speed_modifier": 0.5,  # 50% speed
        "can_stack": False,
        "max_stacks": 1,
        "description": "Speed reduced by 50%",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 0.5,
    },
    "weakened": {
        "type": StatusType.DEBUFF,
        "flags": [],
        "default_duration": 20,
        "default_tick_rate": 0,
        "damage_reduction": 30,  # -30% damage
        "can_stack": False,
        "max_stacks": 1,
        "description": "Damage output reduced by 30%",
        "combat_penalty": 0,
        "damage_mod_out": 0.7,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "rooted": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.ROOTED],
        "default_duration": 5,
        "default_tick_rate": 0,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Cannot teleport or move",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 0.0,  # Cannot move
    },
    "burning": {
        "type": StatusType.DEBUFF,
        "flags": [],
        "default_duration": 12,
        "default_tick_rate": 2,
        "damage_per_tick": 35,
        "can_stack": True,
        "max_stacks": 3,
        "description": "Takes fire damage each tick",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "frozen": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.STUN, StatusFlag.PARALYSIS],
        "default_duration": 4,
        "default_tick_rate": 0,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Frozen solid - cannot act",
        "combat_penalty": 100,
        "damage_mod_out": 0.0,
        "damage_mod_in": 1.5,  # Takes more damage while frozen
        "speed_mod": 0.0,
    },
    "electrocuted": {
        "type": StatusType.DEBUFF,
        "flags": [StatusFlag.PARALYSIS],
        "default_duration": 3,
        "default_tick_rate": 1,
        "damage_per_tick": 25,
        "can_stack": True,
        "max_stacks": 2,
        "description": "Takes electrical damage, partial paralysis",
        "combat_penalty": 50,
        "damage_mod_out": 0.8,
        "damage_mod_in": 1.0,
        "speed_mod": 0.5,
    },

    # ==================== BUFFS ====================
    "regen": {
        "type": StatusType.BUFF,
        "flags": [StatusFlag.REGEN],
        "default_duration": 30,
        "default_tick_rate": 5,
        "heal_per_tick": 25,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Heals HP each tick",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "super_regen": {
        "type": StatusType.BUFF,
        "flags": [StatusFlag.REGEN],
        "default_duration": 45,
        "default_tick_rate": 3,
        "heal_per_tick": 50,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Heals HP rapidly each tick",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "haste": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 20,
        "default_tick_rate": 0,
        "speed_modifier": 1.5,
        "cooldown_reduction": 25,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Speed increased by 50%, cooldowns reduced by 25%",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.5,
    },
    "shield": {
        "type": StatusType.BUFF,
        "flags": [StatusFlag.INVULNERABLE],
        "default_duration": 15,
        "default_tick_rate": 0,
        "shield_absorption": 100,
        "shield_type": "physical_ki",  # Blocks both
        "can_stack": False,
        "max_stacks": 1,
        "description": "Absorbs all incoming damage",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 0.0,  # Blocks all damage
        "speed_mod": 1.0,
    },
    "ki_shield": {
        "type": StatusType.BUFF,
        "flags": [StatusFlag.INVULNERABLE],
        "default_duration": 20,
        "default_tick_rate": 0,
        "shield_absorption": 150,
        "shield_type": "ki",  # Blocks ki attacks only
        "can_stack": False,
        "max_stacks": 1,
        "description": "Absorbs ki damage (150 HP worth)",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 0.0,
        "speed_mod": 1.0,
    },
    "reflect": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 15,
        "default_tick_rate": 0,
        "reflect_percent": 40,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Returns 40% of ki damage to attacker",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "invisibility": {
        "type": StatusType.BUFF,
        "flags": [StatusFlag.INVISIBLE],
        "default_duration": 25,
        "default_tick_rate": 0,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Cannot be sensed or targeted (breaks on attack)",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "ki_boost": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 30,
        "default_tick_rate": 0,
        "damage_boost": 40,  # +40% ki damage
        "can_stack": False,
        "max_stacks": 1,
        "description": "Ki attacks deal 40% more damage",
        "combat_penalty": 0,
        "damage_mod_out": 1.4,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "strength_boost": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 30,
        "default_tick_rate": 0,
        "damage_boost": 40,  # +40% melee damage
        "can_stack": False,
        "max_stacks": 1,
        "description": "Melee attacks deal 40% more damage",
        "combat_penalty": 0,
        "damage_mod_out": 1.4,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "endure": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 25,
        "default_tick_rate": 0,
        "damage_reduction": 40,  # -40% incoming
        "can_stack": False,
        "max_stacks": 1,
        "description": "Reduces all incoming damage by 40%",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 0.6,
        "speed_mod": 1.0,
    },
    "iron_body": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 20,
        "default_tick_rate": 0,
        "damage_reduction": 50,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Reduces incoming damage by 50%",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 0.5,
        "speed_mod": 1.0,
    },
    "critical_boost": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 30,
        "default_tick_rate": 0,
        "crit_chance_boost": 25,  # +25% crit chance
        "can_stack": False,
        "max_stacks": 1,
        "description": "Critical hit chance increased by 25%",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 1.0,
    },
    "zanzoken": {
        "type": StatusType.BUFF,
        "flags": [],
        "default_duration": 15,
        "default_tick_rate": 0,
        "speed_modifier": 2.0,
        "dodge_bonus": 30,
        "can_stack": False,
        "max_stacks": 1,
        "description": "Double speed, 30% dodge chance",
        "combat_penalty": 0,
        "damage_mod_out": 1.0,
        "damage_mod_in": 1.0,
        "speed_mod": 2.0,
    },
}


@dataclass
class ActiveStatus:
    """
    Represents an active status effect on a character.
    
    Attributes:
        status_key: The status effect type (e.g., "poison", "regen")
        duration: Remaining duration in seconds
        max_duration: Original duration (for display)
        tick_rate: How often the effect ticks (0 = no tick)
        damage_per_tick: Damage dealt each tick (for damage effects)
        heal_per_tick: Healing each tick (for heal effects)
        stacks: Number of stacks of this effect
        applied_at: Timestamp when applied
        last_tick: Timestamp of last tick
        attacker: Who applied this effect (for tracking credit)
        source: What technique/ability applied this
        metadata: Additional effect-specific data
    """
    status_key: str
    duration: float
    max_duration: float
    tick_rate: float = 0
    damage_per_tick: int = 0
    heal_per_tick: int = 0
    stacks: int = 1
    applied_at: float = field(default_factory=time.time)
    last_tick: float = field(default_factory=time.time)
    attacker_id: Optional[int] = None
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def tick(self) -> bool:
        """
        Process a tick of this status effect.
        Returns True if damage/healing should be applied.
        """
        current_time = time.time()
        if current_time - self.last_tick >= self.tick_rate and self.tick_rate > 0:
            self.last_tick = current_time
            return True
        return False


def _ensure_status_storage(character) -> Dict[str, ActiveStatus]:
    """Ensure character has status storage initialized."""
    if not hasattr(character.db, 'status_effects') or character.db.status_effects is None:
        character.db.status_effects = {}
    return character.db.status_effects


def apply_status(
    character,
    status_key: str,
    duration: Optional[float] = None,
    tick_rate: Optional[float] = None,
    damage_per_tick: Optional[int] = None,
    heal_per_tick: Optional[int] = None,
    stacks: int = 1,
    attacker=None,
    source: str = "",
    **metadata
) -> bool:
    """
    Apply a status effect to a character.
    
    Args:
        character: The character to apply the effect to
        status_key: The status effect type (must be in STATUS_DEFINITIONS)
        duration: Duration in seconds (uses default if not specified)
        tick_rate: How often to tick (uses default if not specified)
        damage_per_tick: Damage per tick (for damage effects)
        heal_per_tick: Healing per tick (for heal effects)
        stacks: Number of stacks to apply
        attacker: Who applied this effect (for credit)
        source: Name of technique/ability that applied this
        **metadata: Additional effect-specific data
    
    Returns:
        True if successfully applied, False if failed (unknown status, immunity, etc.)
    
    Example:
        # Apply poison to target
        apply_status(target, "poison", duration=20, damage_per_tick=30, 
                     attacker=attacker, source="toxic_claw")
        
        # Apply regen to self
        apply_status(caster, "regen", duration=30, heal_per_tick=25)
    """
    # Validate status exists
    if status_key not in STATUS_DEFINITIONS:
        return False
    
    status_def = STATUS_DEFINITIONS[status_key]
    current_time = time.time()
    
    # Get existing status or create new
    statuses = _ensure_status_storage(character)
    existing = statuses.get(status_key)
    
    # Check stacking rules
    if existing and not status_def.get("can_stack", False):
        # Refresh duration instead of stacking
        existing.duration = duration if duration is not None else status_def["default_duration"]
        existing.max_duration = existing.duration
        existing.applied_at = current_time
        existing.last_tick = current_time
        if attacker:
            existing.attacker_id = attacker.id
        if source:
            existing.source = source
        character.msg(f"|gThe {status_key} effect has been refreshed!|n")
        return True
    
    # Handle stacking
    if existing:
        max_stacks = status_def.get("max_stacks", 1)
        if existing.stacks < max_stacks:
            existing.stacks = min(existing.stacks + stacks, max_stacks)
            existing.duration = duration if duration is not None else status_def["default_duration"]
            existing.max_duration = existing.duration
            existing.applied_at = current_time
            character.msg(f"|g{status_key.title()} stacks increased to {existing.stacks}!|n")
        else:
            # At max stacks, just refresh
            existing.duration = duration if duration is not None else status_def["default_duration"]
            existing.max_duration = existing.duration
            existing.applied_at = current_time
    else:
        # Create new status
        new_status = ActiveStatus(
            status_key=status_key,
            duration=duration if duration is not None else status_def["default_duration"],
            max_duration=duration if duration is not None else status_def["default_duration"],
            tick_rate=tick_rate if tick_rate is not None else status_def.get("default_tick_rate", 0),
            damage_per_tick=damage_per_tick if damage_per_tick is not None else status_def.get("damage_per_tick", 0),
            heal_per_tick=heal_per_tick if heal_per_tick is not None else status_def.get("heal_per_tick", 0),
            stacks=stacks,
            applied_at=current_time,
            last_tick=current_time,
            attacker_id=attacker.id if attacker else None,
            source=source,
            metadata=metadata
        )
        statuses[status_key] = new_status
    
    # Announce status application
    status_type = status_def.get("type", StatusType.NEUTRAL)
    if status_type == StatusType.DEBUFF:
        character.msg(f"|rYou are now affected by {status_key}!|n")
    elif status_type == StatusType.BUFF:
        character.msg(f"|gYou are now affected by {status_key}!|n")
    
    return True


def remove_status(character, status_key: str) -> bool:
    """
    Remove a specific status effect from a character.
    
    Args:
        character: The character to remove the effect from
        status_key: The status effect type to remove
    
    Returns:
        True if removed, False if not present
    
    Example:
        remove_status(target, "poison")
    """
    statuses = _ensure_status_storage(character)
    if status_key in statuses:
        del statuses[status_key]
        character.msg(f"|yThe {status_key} effect has worn off.|n")
        return True
    return False


def remove_all_debuffs(character) -> int:
    """
    Remove all debuffs from a character (e.g., when cleansed).
    
    Returns:
        Number of debuffs removed
    """
    statuses = _ensure_status_storage(character)
    removed = 0
    for key, status in list(statuses.items()):
        if STATUS_DEFINITIONS.get(key, {}).get("type") == StatusType.DEBUFF:
            del statuses[key]
            removed += 1
    if removed > 0:
        character.msg(f"|gAll debuffs have been removed! ({removed} effects)|n")
    return removed


def remove_all_buffs(character) -> int:
    """
    Remove all buffs from a character (e.g., when dispel is used).
    
    Returns:
        Number of buffs removed
    """
    statuses = _ensure_status_storage(character)
    removed = 0
    for key, status in list(statuses.items()):
        if STATUS_DEFINITIONS.get(key, {}).get("type") == StatusType.BUFF:
            del statuses[key]
            removed += 1
    if removed > 0:
        character.msg(f"|rAll buffs have been dispelled! ({removed} effects)|n")
    return removed


def has_status(character, status_key: str) -> bool:
    """
    Check if a character has a specific status effect.
    
    Args:
        character: The character to check
        status_key: The status effect type to check for
    
    Returns:
        True if character has the status, False otherwise
    
    Example:
        if has_status(enemy, "stun"):
            attacker.msg("They are stunned!")
    """
    statuses = _ensure_status_storage(character)
    return status_key in statuses


def has_any_status_of_type(character, status_type: StatusType) -> bool:
    """
    Check if a character has any status of a specific type.
    
    Args:
        character: The character to check
        status_type: The type of status to check for
    
    Returns:
        True if character has any matching status
    """
    statuses = _ensure_status_storage(character)
    for key in statuses:
        if STATUS_DEFINITIONS.get(key, {}).get("type") == status_type:
            return True
    return False


def get_active_statuses(character, status_type: Optional[StatusType] = None) -> List[ActiveStatus]:
    """
    Get all active status effects on a character.
    
    Args:
        character: The character to get statuses from
        status_type: Filter by type (DEBUFF, BUFF, or None for all)
    
    Returns:
        List of ActiveStatus objects
    
    Example:
        # Get all debuffs
        debuffs = get_active_statuses(target, StatusType.DEBUFF)
        for debuff in debuffs:
            attacker.msg(f"Target has: {debuff.status_key}")
    """
    statuses = _ensure_status_storage(character)
    if status_type is None:
        return list(statuses.values())
    return [s for s in statuses.values() if STATUS_DEFINITIONS.get(s.status_key, {}).get("type") == status_type]


def get_status_modifier(character, modifier_type: str) -> float:
    """
    Get the cumulative modifier from all active statuses for a stat.
    
    Args:
        character: The character to check
        modifier_type: The type of modifier ("damage_out", "damage_in", "speed", "accuracy")
    
    Returns:
        Multiplier for the requested stat (1.0 = no modifier)
    
    Example:
        # Get incoming damage modifier (includes buffs and debuffs)
        damage_multiplier = get_status_modifier(target, "damage_in")
        final_damage = base_damage * damage_multiplier
    """
    statuses = _ensure_status_storage(character)
    multiplier = 1.0
    
    for status_key, status in statuses.items():
        status_def = STATUS_DEFINITIONS.get(status_key, {})
        
        if modifier_type == "damage_out":
            # Outgoing damage modifier
            mult = status_def.get("damage_mod_out", 1.0)
            boost = status_def.get("damage_boost", 0)
            if boost:
                mult = 1.0 + (boost / 100.0)
            multiplier *= mult
            
        elif modifier_type == "damage_in":
            # Incoming damage modifier
            mult = status_def.get("damage_mod_in", 1.0)
            reduction = status_def.get("damage_reduction", 0)
            if reduction:
                mult = 1.0 - (reduction / 100.0)
            multiplier *= mult
            
        elif modifier_type == "speed":
            # Speed modifier
            speed_mod = status_def.get("speed_mod", 1.0)
            custom_speed = status_def.get("speed_modifier", 0)
            if custom_speed:
                speed_mod = custom_speed
            multiplier *= speed_mod
            
        elif modifier_type == "accuracy":
            # Accuracy modifier (for blind)
            acc_penalty = status_def.get("accuracy_penalty", 0)
            if acc_penalty:
                multiplier *= (1.0 - (acc_penalty / 100.0))
    
    return max(0.1, multiplier)  # Minimum 10% effectiveness


def can_act(character) -> tuple[bool, str]:
    """
    Check if a character can act in combat (not stunned, paralyzed, etc.).
    
    Returns:
        Tuple of (can_act, reason_if_not)
    
    Example:
        can, reason = can_act(target)
        if not can:
            attacker.msg(f"Cannot target them: {reason}")
    """
    statuses = _ensure_status_storage(character)
    
    # Check for stun
    if has_status(character, "stun"):
        return False, "stunned"
    
    # Check for paralysis
    if has_status(character, "paralysis"):
        return False, "paralyzed"
    
    # Check for frozen
    if has_status(character, "frozen"):
        return False, "frozen"
    
    # Check for electrocuted (partial penalty)
    if has_status(character, "electrocuted"):
        return True, ""  # Can act but at penalty
    
    return True, ""


def can_use_ki(character) -> bool:
    """
    Check if a character can use ki techniques (not silenced).
    
    Returns:
        True if can use ki, False if silenced
    """
    return not has_status(character, "silence")


def can_move(character) -> bool:
    """
    Check if a character can move (not rooted, paralyzed, frozen).
    
    Returns:
        True if can move, False otherwise
    """
    if has_status(character, "rooted"):
        return False
    if has_status(character, "paralysis"):
        return False
    if has_status(character, "frozen"):
        return False
    return True


def can_be_targeted(character) -> bool:
    """
    Check if a character can be targeted (not shielded, invulnerable).
    
    Returns:
        True if can be targeted, False otherwise
    """
    # Check for shield that makes fully invulnerable
    statuses = _ensure_status_storage(character)
    for status_key in statuses:
        status_def = STATUS_DEFINITIONS.get(status_key, {})
        if StatusFlag.INVULNERABLE in status_def.get("flags", []):
            shield_abs = status_def.get("shield_absorption", 0)
            # Check if shield still has absorption
            if shield_abs > 0:
                return False
    
    # Check for invisibility
    if has_status(character, "invisibility"):
        return False
    
    return True


def get_status_display(character) -> str:
    """
    Get a formatted display of all active status effects.
    
    Returns:
        Formatted string of all statuses with durations
    """
    statuses = _ensure_status_storage(character)
    if not statuses:
        return "|yNo active status effects.|n"
    
    lines = ["|yActive Status Effects:|n"]
    for key, status in statuses.items():
        status_def = STATUS_DEFINITIONS.get(key, {})
        status_type = status_def.get("type", StatusType.NEUTRAL)
        
        # Color by type
        if status_type == StatusType.DEBUFF:
            color = "|r"
        elif status_type == StatusType.BUFF:
            color = "|g"
        else:
            color = "|y"
        
        # Build status line
        duration_str = f"{status.duration:.1f}s"
        if status.stacks > 1:
            stacks_str = f" (x{status.stacks})"
        else:
            stacks_str = ""
        
        # Add tick info if applicable
        if status.damage_per_tick > 0:
            tick_str = f" | {status.damage_per_tick}dmg/tick"
        elif status.heal_per_tick > 0:
            tick_str = f" | +{status.heal_per_tick}hp/tick"
        else:
            tick_str = ""
        
        lines.append(f"  {color}{key.title()}|n: {duration_str}{stacks_str}{tick_str}")
    
    return "".join(lines)


def tick_status_effects(character) -> Dict[str, Any]:
    """
    Process all status effects on a character - called every second by combat handler.
    
    This function:
    1. Decreases duration of all effects
    2. Processes tick effects (damage/healing)
    3. Removes expired effects
    4. Returns summary of effects applied
    
    Args:
        character: The character to process effects for
    
    Returns:
        Dict with "damage", "healing", "expired", "applied" lists
    
    Example:
        # Called from combat handler tick
        results = tick_status_effects(character)
        if results["damage"]:
            character.msg("|rYou take damage from status effects!|n")
    """
    statuses = _ensure_status_storage(character)
    results = {
        "damage": [],      # (amount, source_status)
        "healing": [],     # (amount, source_status)
        "expired": [],     # status_keys that expired
        "applied": []     # statuses that had ticks this frame
    }
    
    current_time = time.time()
    expired = []
    
    for status_key, status in list(statuses.items()):
        status_def = STATUS_DEFINITIONS.get(status_key, {})
        
        # Decrease duration
        status.duration -= 1.0
        
        # Check for tick
        if status.tick():
            # Apply tick damage
            if status.damage_per_tick > 0:
                dmg = status.damage_per_tick * status.stacks
                results["damage"].append((dmg, status_key))
                character.msg(f"|r{status_key.title()} deals {dmg} damage!|n")
            
            # Apply tick healing
            if status.heal_per_tick > 0:
                heal = status.heal_per_tick * status.stacks
                results["healing"].append((heal, status_key))
                character.msg(f"|g{status_key.title()} heals {heal} HP!|n")
            
            results["applied"].append(status_key)
        
        # Check for expiration
        if status.duration <= 0:
            expired.append(status_key)
    
    # Remove expired statuses
    for status_key in expired:
        del statuses[status_key]
        results["expired"].append(status_key)
        character.msg(f"|yThe {status_key} effect has worn off.|n")
    
    return results


def apply_status_from_technique(attacker, target, technique_key: str) -> bool:
    """
    Apply status effects based on a technique's effect_data.
    
    This is called from the combat system when a technique hits.
    
    Args:
        attacker: The character using the technique
        target: The target of the technique
        technique_key: The key of the technique being used
    
    Returns:
        True if any status was applied, False otherwise
    
    Example:
        # In combat resolution:
        apply_status_from_technique(attacker, target, "toxic_claw")
    """
    from world.techniques import TECHNIQUES
    
    tech = TECHNIQUES.get(technique_key)
    if not tech:
        return False
    
    effect_data = tech.get("effect_data", {})
    if not effect_data:
        return False
    
    status_key = effect_data.get("status")
    if not status_key:
        return False
    
    # Check if this attack type can apply this status
    sources = effect_data.get("sources", ["melee", "ki"])
    attack_type = tech.get("type", "melee")
    if attack_type not in sources:
        return False
    
    # Apply the status
    duration = effect_data.get("duration")
    tick_rate = effect_data.get("tick_rate")
    damage_per_tick = effect_data.get("damage_per_tick")
    
    return apply_status(
        target,
        status_key,
        duration=duration,
        tick_rate=tick_rate,
        damage_per_tick=damage_per_tick,
        attacker=attacker,
        source=technique_key
    )


# Status effect technique mappings - which techniques apply which effects
STATUS_TECHNIQUE_MAP = {
    # Debuff-applying techniques
    "toxic_claw": {"status": "poison", "chance": 40},
    "deadly_poison": {"status": "poison", "chance": 60},
    " paralysis_wave": {"status": "paralysis", "chance": 30},
    "thunder_fist": {"status": "electrocuted", "chance": 50},
    "ice_beam": {"status": "frozen", "chance": 35},
    "blinding_rush": {"status": "blind", "chance": 40},
    "silencing_voice": {"status": "silence", "chance": 45},
    "root_wave": {"status": "rooted", "chance": 35},
    "weakening_strike": {"status": "weakened", "chance": 50},
    "fire_ball": {"status": "burning", "chance": 45},
    "dragon_hammer": {"status": "bleeding", "chance": 35},
    
    # Buff-applying techniques
    "marble_jet": {"status": "regen", "chance": 100},
    "godly_recovery": {"status": "super_regen", "chance": 100},
    "energy_shield": {"status": "shield", "chance": 100},
    "ki_barrier": {"status": "ki_shield", "chance": 100},
    "mirror_technique": {"status": "reflect", "chance": 100},
    "instant_transmission": {"status": "zanzoken", "chance": 100},
    "kiai": {"status": "endure", "chance": 100},
    "power_technique": {"status": "strength_boost", "chance": 100},
    "ki_technique": {"status": "ki_boost", "chance": 100},
    "eyes_of_granola": {"status": "critical_boost", "chance": 100},
    "spirit_bomb": {"status": "regen", "chance": 100},  # Self-heal after big attack
}


def try_apply_status_from_technique(attacker, target, technique_key: str) -> bool:
    """
    Try to apply a status effect from a technique with chance-based application.
    
    Args:
        attacker: The character using the technique
        target: The target of the technique
        technique_key: The key of the technique being used
    
    Returns:
        True if status was applied, False otherwise
    
    Example:
        # Called when a technique hits
        applied = try_apply_status_from_technique(attacker, target, "toxic_claw")
        if applied:
            attacker.msg("You poison your target!")
    """
    status_info = STATUS_TECHNIQUE_MAP.get(technique_key)
    if not status_info:
        # Try to get from technique definition directly
        return apply_status_from_technique(attacker, target, technique_key)
    
    # Check chance
    chance = status_info.get("chance", 0)
    if random.randint(1, 100) > chance:
        return False
    
    # Apply the status
    status_key = status_info.get("status")
    status_def = STATUS_DEFINITIONS.get(status_key, {})
    
    return apply_status(
        target,
        status_key,
        duration=status_def.get("default_duration"),
        tick_rate=status_def.get("default_tick_rate"),
        damage_per_tick=status_def.get("damage_per_tick"),
        heal_per_tick=status_def.get("heal_per_tick"),
        attacker=attacker,
        source=technique_key
    )


# Console command helpers
def get_all_status_info() -> str:
    """Get a formatted list of all available status effects."""
    lines = ["|y=== Available Status Effects ===|n|n"]
    
    lines.append("|rDEBUFFS:|n")
    for key, defn in STATUS_DEFINITIONS.items():
        if defn.get("type") == StatusType.DEBUFF:
            lines.append(f"  |r{key}|n: {defn.get('description', 'No description')}")
    
    lines.append("\n|yBUFFS:|n")
    for key, defn in STATUS_DEFINITIONS.items():
        if defn.get("type") == StatusType.BUFF:
            lines.append(f"  |g{key}|n: {defn.get('description', 'No description')}")
    
    return "".join(lines)
