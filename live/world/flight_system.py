"""
================================================================================
FLIGHT SYSTEM - DBForged Vertical Slice
================================================================================

This module provides a comprehensive flight system for DBZ-themed gameplay.
Players can fly, hover, and travel through the skies.

FLIGHT STATES:
--------------
1. GROUND - Normal movement, on foot
2. LEVITATE - Can move over water/gaps (requires 1000 PL)
3. FLYING - Full flight, 2x movement speed (requires 5000 PL)
4. SUPER_SPEED - 3x speed, fly over obstacles (requires 50000 PL)

FLIGHT COMMANDS:
----------------
fly              - Take to the skies
fly <direction>  - Fly in a direction with animation
fly to <place>   - Fast travel (if unlocked)
land             - Return to ground
flight status    - Check flight status

MECHANICS:
----------
- Flight requires ki to maintain (drains over time)
- Higher flight states drain ki faster
- Landing in combat is risky (can be attacked)
- Flight speed affects travel time
- Can fly over water, gaps, small obstacles

FLIGHT TRAINING:
----------------
- Training zones to increase flight skill
- Higher skill = less ki drain
- Unlock new flight states at PL thresholds

Example Usage:
-------------
# Basic flight
fly

# Fly somewhere
fly north

# Land
land

# Check status
flight status
"""

from __future__ import annotations

import time
import random
from typing import Dict, List, Optional, Any
from enum import Enum


class FlightState(Enum):
    """Flight state levels."""
    GROUND = "ground"
    LEVITATE = "levitate"
    FLYING = "flying"
    SUPER_SPEED = "super_speed"


# Flight state requirements
FLIGHT_REQUIREMENTS = {
    FlightState.GROUND: {"pl": 0, "ki_drain": 0},
    FlightState.LEVITATE: {"pl": 1000, "ki_drain": 1},
    FlightState.FLYING: {"pl": 5000, "ki_drain": 3},
    FlightState.SUPER_SPEED: {"pl": 50000, "ki_drain": 5},
}

# Flight speed multipliers
FLIGHT_SPEEDS = {
    FlightState.GROUND: 1.0,
    FlightState.LEVITATE: 1.2,
    FlightState.FLYING: 2.0,
    FlightState.SUPER_SPEED: 3.0,
}

# Flight messages by state
FLIGHT_MESSAGES = {
    "take_off": {
        FlightState.LEVITATE: "You gently rise into the air, floating above the ground.",
        FlightState.FLYING: "You burst upward, soaring into the sky with incredible speed!",
        FlightState.SUPER_SPEED: "You vanish in a flash, appearing high above as a golden streak!",
    },
    "fly": {
        FlightState.LEVITATE: "You float",
        FlightState.FLYING: "You soar through the air",
        FlightState.SUPER_SPEED: "You blur through the sky",
    },
    "land": {
        FlightState.LEVITATE: "You slowly descend to the ground.",
        FlightState.FLYING: "You glide down, touching the ground with a soft landing.",
        FlightState.SUPER_SPEED: "You slow to a stop, descending from the skies.",
    },
}


def can_fly(character) -> tuple[bool, str]:
    """
    Check if character can fly.
    
    Args:
        character: The character to check
    
    Returns:
        Tuple of (can_fly, reason)
    """
    pl = character.db.get('power_level', 0)
    
    if pl < FLIGHT_REQUIREMENTS[FlightState.LEVITATE]["pl"]:
        return False, f"You need at least {FLIGHT_REQUIREMENTS[FlightState.LEVITATE]['pl']} PL to even levitate."
    
    return True, ""


def can_super_speed(character) -> tuple[bool, str]:
    """Check if character can use super speed."""
    pl = character.db.get('power_level', 0)
    if pl < FLIGHT_REQUIREMENTS[FlightState.SUPER_SPEED]["pl"]:
        return False, "You need 50,000 PL to use Super Speed."
    return True, ""


def get_flight_state(character) -> FlightState:
    """Get current flight state of character."""
    state = character.db.get('flight_state')
    if state:
        return FlightState(state)
    return FlightState.GROUND


def set_flight_state(character, state: FlightState) -> bool:
    """
    Set character's flight state.
    
    Args:
        character: The character
        state: The flight state to set
    
    Returns:
        True if successful
    """
    pl = character.db.get('power_level', 0)
    required_pl = FLIGHT_REQUIREMENTS[state]["pl"]
    
    if pl < required_pl:
        return False
    
    character.db.flight_state = state.value
    return True


def take_off(character, target_state: FlightState = None) -> tuple[bool, str]:
    """
    Take off into the air.
    
    Args:
        character: The character taking off
        target_state: Desired flight state (auto-selected if None)
    
    Returns:
        Tuple of (success, message)
    """
    current_state = get_flight_state(character)
    if current_state != FlightState.GROUND:
        return False, "You're already in the air!"
    
    pl = character.db.get('power_level', 0)
    
    # Determine best available state
    if target_state is None:
        if pl >= FLIGHT_REQUIREMENTS[FlightState.SUPER_SPEED]["pl"]:
            target_state = FlightState.SUPER_SPEED
        elif pl >= FLIGHT_REQUIREMENTS[FlightState.FLYING]["pl"]:
            target_state = FlightState.FLYING
        elif pl >= FLIGHT_REQUIREMENTS[FlightState.LEVITATE]["pl"]:
            target_state = FlightState.LEVITATE
        else:
            return False, "You can't even levitate yet!"
    
    # Check PL requirement
    required_pl = FLIGHT_REQUIREMENTS[target_state]["pl"]
    if pl < required_pl:
        return False, f"You need {required_pl:,} PL to {target_state.value}."
    
    # Set state
    character.db.flight_state = target_state.value
    
    # Get message
    message = FLIGHT_MESSAGES["take_off"].get(target_state, "You rise into the air.")
    
    return True, f"|c{message}|n"


def land(character) -> tuple[bool, str]:
    """
    Land on the ground.
    
    Args:
        character: The character landing
    
    Returns:
        Tuple of (success, message)
    """
    current_state = get_flight_state(character)
    
    if current_state == FlightState.GROUND:
        return False, "You're already on the ground."
    
    # Check if in combat (risky landing)
    in_combat = character.db.get('in_combat', False)
    if in_combat:
        # Chance to be attacked while landing
        if random.randint(1, 100) <= 30:
            character.msg("|rYou are attacked while landing!|n")
            # Could trigger combat here
    
    # Set to ground
    character.db.flight_state = FlightState.GROUND.value
    
    # Get message
    message = FLIGHT_MESSAGES["land"].get(current_state, "You land on the ground.")
    
    return True, f"|c{message}|n"


def fly_direction(character, direction: str) -> tuple[bool, str]:
    """
    Fly in a direction.
    
    Args:
        character: The flying character
        direction: Direction to fly (north, south, east, west, up, down)
    
    Returns:
        Tuple of (success, message)
    """
    current_state = get_flight_state(character)
    
    if current_state == FlightState.GROUND:
        return False, "You need to take off first! Use 'fly'."
    
    # Get room exits
    location = character.location
    if not location:
        return False, "You have no location."
    
    # Check if direction is valid
    exits = location.exits
    direction_map = {
        "n": "north", "north": "north",
        "s": "south", "south": "south", 
        "e": "east", "east": "east",
        "w": "west", "west": "west",
        "u": "up", "up": "up",
        "d": "down", "down": "down",
    }
    
    normalized_dir = direction_map.get(direction.lower(), direction)
    
    # Find matching exit
    target_exit = None
    for exit_obj in exits:
        if exit_obj.key.lower() == normalized_dir:
            target_exit = exit_obj
            break
    
    if not target_exit:
        return False, f"You can't fly {direction} from here."
    
    # Check if direction requires flight (up, or over water/gaps)
    # For now, allow flying in any direction
    
    # Drain ki while flying
    ki_drain = FLIGHT_REQUIREMENTS[current_state]["ki_drain"]
    current_ki = character.db.get('ki', 100)
    max_ki = character.db.get('max_ki', 100)
    
    if current_ki < ki_drain:
        character.msg("|yYou don't have enough ki to maintain flight!|n")
        # Auto-land
        return land(character)
    
    # Deduct ki
    character.db.ki = max(0, current_ki - ki_drain)
    
    # Get fly message
    fly_msg = FLIGHT_MESSAGES["fly"].get(current_state, "You fly")
    
    # Move to new room
    character.move_to(target_exit)
    
    # Arrival message
    speed_name = current_state.value
    return True, f"|c{fly_msg} {normalized_dir}!|n"


def get_flight_status(character) -> str:
    """
    Get formatted flight status.
    
    Args:
        character: The character
    
    Returns:
        Formatted status string
    """
    current_state = get_flight_state(character)
    pl = character.db.get('power_level', 0)
    current_ki = character.db.get('ki', 100)
    max_ki = character.db.get('max_ki', 100)
    
    lines = ["|c=== FLIGHT STATUS ===|n"]
    
    lines.append(f"Current State: |w{current_state.value.upper()}|n")
    
    if current_state != FlightState.GROUND:
        speed = FLIGHT_SPEEDS[current_state]
        ki_drain = FLIGHT_REQUIREMENTS[current_state]["ki_drain"]
        
        lines.append(f"Speed: {speed}x normal")
        lines.append(f"KI Drain: {ki_drain}/move")
        lines.append(f"Current KI: {current_ki}/{max_ki}")
    
    # Show available states
    lines.append("\n|wAvailable Flight States:|n")
    
    for state in FlightState:
        required_pl = FLIGHT_REQUIREMENTS[state]["pl"]
        if pl >= required_pl:
            status = "|g✓|n" if current_state == state else "|x |n"
            lines.append(f"  {status} {state.value.title()} ({required_pl:,} PL)")
        else:
            lines.append(f"  |r✗|n {state.value.title()} ({required_pl:,} PL)")
    
    return "".join(lines)


def process_flight_drain(character) -> bool:
    """
    Process ongoing flight ki drain.
    Called every few seconds while flying.
    
    Args:
        character: The flying character
    
    Returns:
        True if still flying, False if landed due to low ki
    """
    current_state = get_flight_state(character)
    
    if current_state == FlightState.GROUND:
        return True
    
    ki_drain = FLIGHT_REQUIREMENTS[current_state]["ki_drain"]
    current_ki = character.db.get('ki', 100)
    
    if current_ki <= ki_drain:
        character.msg("|yYou don't have enough ki to fly!|n")
        land(character)
        return False
    
    character.db.ki = current_ki - ki_drain
    return True


# =============================================================================
# FAST TRAVEL SYSTEM
# =============================================================================

# Fast travel unlock requirements
FAST_TRAVEL_POINTS = {
    "kame_island": {
        "name": "Kame House",
        "pl_required": 0,
        "cost": 0,
        "description": "Turtle Hermit's island",
    },
    "capsule_corp": {
        "name": "Capsule Corp",
        "pl_required": 5000,
        "cost": 0,
        "description": "Bulma's company in West City",
    },
    "lookout": {
        "name": "Kami's Lookout",
        "pl_required": 10000,
        "cost": 0,
        "description": "Floating checkpoint above Earth",
    },
    "planet_vegeta": {
        "name": "Planet Vegeta",
        "pl_required": 25000,
        "cost": 0,
        "description": "The ruined Saiyan homeworld",
        "faction": "saiyan_army",
    },
    "namek": {
        "name": "Namek",
        "pl_required": 30000,
        "cost": 0,
        "description": "The Namekian homeworld",
        "faction": "namekian_clan",
    },
    "Otherworld": {
        "name": "Otherworld",
        "pl_required": 50000,
        "cost": 0,
        "description": "The realm beyond",
        "quest": "kaios_trial",
    },
}


def unlock_fast_travel(character, location_key: str) -> bool:
    """
    Unlock a fast travel location for a character.
    
    Args:
        character: The character
        location_key: The fast travel point key
    
    Returns:
        True if unlocked
    """
    if location_key not in FAST_TRAVEL_POINTS:
        return False
    
    # Get or create unlocked list
    unlocked = character.db.get('fast_travel_unlocked', [])
    if location_key in unlocked:
        return True  # Already unlocked
    
    # Check requirements
    location = FAST_TRAVEL_POINTS[location_key]
    pl = character.db.get('power_level', 0)
    
    if pl < location.get('pl_required', 0):
        return False
    
    # Check faction requirement
    if 'faction' in location:
        if character.db.get('faction') != location['faction']:
            return False
    
    # Check quest requirement
    if 'quest' in location:
        completed_quests = character.db.get('completed_quests', [])
        if location['quest'] not in completed_quests:
            return False
    
    # Unlock
    unlocked.append(location_key)
    character.db.fast_travel_unlocked = unlocked
    
    return True


def fly_to_location(character, location_key: str) -> tuple[bool, str]:
    """
    Fast travel to a location via flight.
    
    Args:
        character: The character
        location_key: The destination key
    
    Returns:
        Tuple of (success, message)
    """
    if location_key not in FAST_TRAVEL_POINTS:
        return False, "Unknown location."
    
    # Check if unlocked
    unlocked = character.db.get('fast_travel_unlocked', [])
    if location_key not in unlocked:
        # Try to unlock
        if not unlock_fast_travel(character, location_key):
            location = FAST_TRAVEL_POINTS[location_key]
            req = location.get('pl_required', 0)
            return False, f"You haven't unlocked {location['name']}. Requires {req:,} PL."
    
    location = FAST_TRAVEL_POINTS[location_key]
    
    # Find the location in-game (would need to link to actual room)
    # For now, just show the travel message
    
    # Check ki cost
    cost = location.get('cost', 0)
    current_ki = character.db.get('ki', 100)
    
    if current_ki < cost:
        return False, f"You need {cost} KI to fly there."
    
    character.db.ki = current_ki - cost
    
    return True, f"|cYou soar through the sky toward {location['name']}...|n"


def get_fast_travel_list(character) -> str:
    """
    Get list of unlocked fast travel points.
    
    Args:
        character: The character
    
    Returns:
        Formatted list
    """
    pl = character.db.get('power_level', 0)
    unlocked = character.db.get('fast_travel_unlocked', [])
    
    lines = ["|y=== FAST TRAVEL POINTS ===|n\n"]
    
    for key, loc in FAST_TRAVEL_POINTS.items():
        req = loc.get('pl_required', 0)
        
        if key in unlocked:
            lines.append(f"|g✓|n {loc['name']}")
        elif pl >= req:
            lines.append(f"|r✗|n {loc['name']} (requires {req:,} PL)")
        else:
            lines.append(f"|x |n {loc['name']} (requires {req:,} PL)")
        
        lines.append(f"    {loc['description']}\n")
    
    return "".join(lines)


# =============================================================================
# FLIGHT COMMANDS
# =============================================================================


class FlightCommand:
    """Flight command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """Handle flight subcommands."""
        args = args.strip().lower() if args else ""
        
        # flight status
        if args == "status":
            return get_flight_status(caller)
        
        # land
        if args == "land":
            success, msg = land(caller)
            return msg if success else f"|r{msg}|n"
        
        # take off
        if args == "" or args == "takeoff" or args == "up":
            current_state = get_flight_state(caller)
            if current_state != FlightState.GROUND:
                return "You're already flying!"
            
            success, msg = take_off(caller)
            return msg if success else f"|r{msg}|n"
        
        # fly somewhere
        if args in ["n", "north", "s", "south", "e", "east", "w", "west", "u", "up", "d", "down"]:
            success, msg = fly_direction(caller, args)
            return msg if success else f"|r{msg}|n"
        
        # fly to location
        if args.startswith("to "):
            location_name = args[3:].strip().lower().replace(" ", "_")
            success, msg = fly_to_location(caller, location_name)
            return msg if success else f"|r{msg}|n"
        
        # fast travel list
        if args == "list" or args == "travel":
            return get_fast_travel_list(caller)
        
        return """|yFlight Commands:|n
  fly              - Take off
  fly north/south/east/west/up/down - Fly in direction
  fly to <place>  - Fast travel (if unlocked)
  land            - Land on ground
  flight status   - Check flight status
  flight list     - Show fast travel points|

Flight States:
  Levitate: 1,000 PL minimum
  Flying: 5,000 PL minimum  
  Super Speed: 50,000 PL minimum|
"""


# Auto-unlock fast travel on PL milestones
def check_fast_travel_unlock(character):
    """Check and unlock fast travel points based on PL."""
    pl = character.db.get('power_level', 0)
    
    for key in FAST_TRAVEL_POINTS:
        unlock_fast_travel(character, key)
