"""
================================================================================
DUNGEON SYSTEM - DBForged Vertical Slice
================================================================================

This module provides themed dungeon gameplay inspired by Dragon Ball locations.

DUNGEONS:
---------
1. MUSCLE TOWER (Red Ribbon Army)
   - Theme: Military fortress
   - Floors: 5
   - Enemies: Red Ribbon soldiers, robots, officers
   - Boss: General Blue
   - Rewards: Red Ribbon gear, zeni, reputation

2. THE CHOSEN 5'S TEST (Kaiō-sama)
   - Theme: Otherworld training
   - Floors: 5  
   - Enemies: Kaiō's guardians, spirit fighters
   - Boss: Āron (Piped)
   - Rewards: Technique mastery, Kaiō badge

3. HEART OF Namek (Namek)
   - Theme: Endangered Namekian village
   - Floors: 3
   - Enemies: Frieza force, villains
   - Boss: Cui or Dodoria
   - Rewards: Namekian crystals, Dragon Ball chance

4. BABA'S HAUNTED MANSION (Otherworld)
   - Theme: Spirit world
   - Floors: 7
   - Enemies: Ghosts, spirits, demons
   - Boss: Ghost Goku (illusion)
   - Rewards: Rare techniques, Baba crystals

5. CAPSULE CORP LAB (West City)
   - Theme: High-tech facility
   - Floors: 4
   - Enemies: Androids, security droids
   - Boss: Android 19 or 20
   - Rewards: Tech blueprints, scouter upgrades

DUNGEON MECHANICS:
------------------
- Each dungeon has multiple floors
- Must defeat all enemies on floor to advance
- Boss on final floor
- Rewards scale with floor number
- Daily reset at midnight
- Partyrecommended for higher floors (3-5)
- Auto-save on entry, can exit anytime

COMMANDS:
---------
- dungeon list - Show available dungeons
- dungeon enter <name> - Enter a dungeon
- dungeon exit - Exit current dungeon
- dungeon floor - Show current floor
- dungeon progress - Show dungeon progress
"""

from __future__ import annotations

import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class DungeonState(Enum):
    """Dungeon entry state."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


# Dungeon Definitions
DUNGEON_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "muscle_tower": {
        "name": "Muscle Tower",
        "theme": "Red Ribbon Army Fortress",
        "description": "A towering fortress filled with Red Ribbon Army soldiers and traps.",
        "difficulty": "medium",
        "floors": 5,
        "recommended_pl": 5000,
        "min_players": 1,
        "max_players": 3,
        "enemies_per_floor": 3,
        "boss": "General Blue",
        "drops": {
            "zeni": (500, 2000),
            "red_ribbon_uniform": (1, 1),
            "zeni_bonus": 25,
            "reputation": "red_ribbon_army",
        },
        "floors": [
            {"name": "Ground Floor", "enemy_tier": "weak", "description": "Guard posts and storage rooms"},
            {"name": "Second Floor", "enemy_tier": "normal", "description": "Soldier barracks"},
            {"name": "Third Floor", "enemy_tier": "normal", "description": "Officer quarters"},
            {"name": "Fourth Floor", "enemy_tier": "strong", "description": "Elite guard station"},
            {"name": "Top Floor", "enemy_tier": "boss", "description": "General Blue's throne room"},
        ],
    },
    "kaios_test": {
        "name": "The Chosen 5's Test",
        "theme": "Otherworld Training",
        "description": "Kaiō-sama's deadly training gauntlet for potential warriors.",
        "difficulty": "hard",
        "floors": 5,
        "recommended_pl": 15000,
        "min_players": 1,
        "max_players": 2,
        "enemies_per_floor": 2,
        "boss": "Āron",
        "drops": {
            "zeni": (1000, 5000),
            "technique_mastery_boost": 10,
            "kaios_blessing": (1, 1),
            "reputation": "kame_house",
        },
        "floors": [
            {"name": "Trial of Courage", "enemy_tier": "normal", "description": "Face your fears"},
            {"name": "Trial of Speed", "enemy_tier": "normal", "description": "Dash through obstacles"},
            {"name": "Trial of Power", "enemy_tier": "strong", "description": "Break through walls"},
            {"name": "Trial of Spirit", "enemy_tier": "strong", "description": "Defeat shadow warriors"},
            {"name": "Trial of the Kaiō", "enemy_tier": "boss", "description": "Face Āron himself"},
        ],
    },
    "namek_heart": {
        "name": "Heart of Namek",
        "theme": "Endangered Village",
        "description": "Defend the Namekian village from Frieza's invading forces.",
        "difficulty": "medium",
        "floors": 3,
        "recommended_pl": 8000,
        "min_players": 1,
        "max_players": 4,
        "enemies_per_floor": 4,
        "boss": "Dodoria",
        "drops": {
            "zeni": (800, 3000),
            "namekian_crystal": (2, 5),
            "dragon_ball_chance": 10,
            "reputation": "namekian_clan",
        },
        "floors": [
            {"name": "Outskirts", "enemy_tier": "normal", "description": "First line of defense"},
            {"name": "Village Center", "enemy_tier": "strong", "description": "Fierce battleground"},
            {"name": "Elder's Shrine", "enemy_tier": "boss", "description": "Dodoria awaits"},
        ],
    },
    "baba_mansion": {
        "name": "Baba's Haunted Mansion",
        "theme": "Otherworld Spirit Realm",
        "description": "Explore the terrifying mansion of the mystic Melinda Baba.",
        "difficulty": "hard",
        "floors": 7,
        "recommended_pl": 20000,
        "min_players": 1,
        "max_players": 3,
        "enemies_per_floor": 3,
        "boss": "Ghost Illusion Goku",
        "drops": {
            "zeni": (2000, 8000),
            "forbidden_technique": (1, 1),
            "baba_crystal": (1, 3),
            "technique_mastery_boost": 15,
        },
        "floors": [
            {"name": "Entrance Hall", "enemy_tier": "weak", "description": "Creaking doors and shadows"},
            {"name": "Dining Room", "enemy_tier": "normal", "description": "Ghostly banquet"},
            {"name": "Library", "enemy_tier": "normal", "description": "Whispering books"},
            {"name": " ballroom", "enemy_tier": "strong", "description": "Dancing specters"},
            {"name": "Laboratory", "enemy_tier": "strong", "description": "Dark experiments"},
            {"name": "Crypt", "enemy_tier": "strong", "description": "Restless dead"},
            {"name": "Throne Room", "enemy_tier": "boss", "description": "Baba awaits"},
        ],
    },
    "capsule_lab": {
        "name": "Capsule Corp Lab",
        "theme": "High-Tech Facility",
        "description": "Infiltrate Dr. Gero's secret laboratory and face the Androids.",
        "difficulty": "hard",
        "floors": 4,
        "recommended_pl": 25000,
        "min_players": 1,
        "max_players": 3,
        "enemies_per_floor": 3,
        "boss": "Android 19",
        "drops": {
            "zeni": (1500, 6000),
            "tech_blueprint": (1, 2),
            "scouter_upgrade": (1, 1),
            "reputation": "capsule_corp",
        },
        "floors": [
            {"name": "Entrance Security", "enemy_tier": "normal", "description": "Security droids"},
            {"name": "Main Lab", "enemy_tier": "strong", "description": "Test subjects"},
            {"name": "Deep Storage", "enemy_tier": "strong", "description": "Dangerous prototypes"},
            {"name": "Control Core", "enemy_tier": "boss", "description": "Face Android 19"},
        ],
    },
}


# Enemy definitions for dungeons
DUNGEON_ENEMIES = {
    "weak": [
        {"name": "Red Ribbon Grunt", "pl": 100, "xp": 50},
        {"name": "Security Drone", "pl": 150, "xp": 75},
        {"name": "Minor Spirit", "pl": 80, "xp": 40},
    ],
    "normal": [
        {"name": "Red Ribbon Soldier", "pl": 500, "xp": 200},
        {"name": "Combat Robot", "pl": 600, "xp": 250},
        {"name": "Guardian Spirit", "pl": 400, "xp": 180},
    ],
    "strong": [
        {"name": "Red Ribbon Officer", "pl": 1500, "xp": 600},
        {"name": "Elite Android", "pl": 2000, "xp": 800},
        {"name": "Wraith Knight", "pl": 1800, "xp": 700},
    ],
    "boss": [
        {"name": "General Blue", "pl": 8000, "xp": 5000},
        {"name": "Āron", "pl": 20000, "xp": 10000},
        {"name": "Dodoria", "pl": 12000, "xp": 8000},
        {"name": "Android 19", "pl": 30000, "xp": 15000},
    ],
}


@dataclass
class DungeonInstance:
    """
    Represents an active dungeon run.
    
    Attributes:
        dungeon_key: The dungeon type
        character_ids: Players in the dungeon
        current_floor: Current floor number (0-indexed)
        enemies_defeated: Total enemies defeated
        enemies_on_floor: Enemies remaining on current floor
        state: Current dungeon state
        entered_at: When dungeon was entered
        floor_started_at: When current floor started
    """
    dungeon_key: str
    character_ids: List[int]
    current_floor: int = 0
    enemies_defeated: int = 0
    enemies_on_floor: int = 0
    state: DungeonState = DungeonState.ACTIVE
    entered_at: float = field(default_factory=time.time)
    floor_started_at: float = field(default_factory=time.time)


# Global dungeon instances - keyed by character ID
_dungeon_instances: Dict[int, DungeonInstance] = {}

# Daily reset tracking
_daily_reset: float = 0


# =============================================================================
# DUNGEON MANAGEMENT
# =============================================================================


def _get_daily_reset_timestamp() -> float:
    """Get timestamp for today's daily reset."""
    from datetime import datetime
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return today.timestamp()


def can_enter_dungeon(character, dungeon_key: str) -> tuple[bool, str]:
    """
    Check if character can enter a dungeon.
    
    Args:
        character: The character
        dungeon_key: The dungeon to enter
    
    Returns:
        Tuple of (can_enter, reason)
    """
    # Check if already in a dungeon
    if character.id in _dungeon_instances:
        return False, "You are already in a dungeon. Exit first."
    
    if dungeon_key not in DUNGEON_DEFINITIONS:
        return False, "Unknown dungeon."
    
    dungeon = DUNGEON_DEFINITIONS[dungeon_key]
    
    # Check PL requirement
    pl = character.db.get('power_level', 0)
    required = dungeon.get('recommended_pl', 0)
    if pl < required * 0.5:  # Allow entry at 50% of recommended
        return False, f"You need at least {int(required * 0.5)} PL to enter {dungeon['name']}."
    
    # Check daily reset
    global _daily_reset
    if _daily_reset < _get_daily_reset_timestamp():
        # New day, reset dungeon entries
        _daily_reset = _get_daily_reset_timestamp()
        character.db.dungeon_entries_today = 0
    
    # Check daily limit
    entries = character.db.get('dungeon_entries_today', 0)
    if entries >= 5:
        return False, "You have used all your dungeon entries today. Come back tomorrow!"
    
    return True, ""


def enter_dungeon(character, dungeon_key: str) -> tuple[bool, str]:
    """
    Enter a dungeon.
    
    Args:
        character: The character entering
        dungeon_key: The dungeon to enter
    
    Returns:
        Tuple of (success, message)
    """
    can_enter, reason = can_enter_dungeon(character, dungeon_key)
    if not can_enter:
        return False, reason
    
    dungeon = DUNGEON_DEFINITIONS[dungeon_key]
    
    # Create dungeon instance
    floor_info = dungeon["floors"][0]
    enemies_per_floor = dungeon.get("enemies_per_floor", 3)
    
    instance = DungeonInstance(
        dungeon_key=dungeon_key,
        character_ids=[character.id],
        current_floor=0,
        enemies_on_floor=enemies_per_floor,
    )
    _dungeon_instances[character.id] = instance
    
    # Track daily entry
    character.db.dungeon_entries_today = character.db.get('dungeon_entries_today', 0) + 1
    
    # Store for returning
    character.db.current_dungeon = dungeon_key
    character.db.dungeon_floor = 0
    
    return True, f"""|g=== {dungeon['name'].upper()} ===|n
{dungeon['description']}

Floor 1/ {dungeon['floors']}: {floor_info['name']}
{floor_info['description']}

Enemies remaining: {enemies_per_floor}
Defeat them all to advance!

Use 'dungeon floor' for details or 'dungeon exit' to leave."""


def exit_dungeon(character) -> tuple[bool, str]:
    """
    Exit current dungeon.
    
    Args:
        character: The character exiting
    
    Returns:
        Tuple of (success, message)
    """
    instance = _dungeon_instances.get(character.id)
    if not instance:
        return False, "You are not in a dungeon."
    
    dungeon = DUNGEON_DEFINITIONS[instance.dungeon_key]
    
    # Calculate rewards for progress
    rewards = _calculate_dungeon_rewards(character, instance)
    
    # Clear instance
    del _dungeon_instances[character.id]
    character.db.current_dungeon = None
    character.db.dungeon_floor = None
    
    return True, f"""|yYou exit {dungeon['name']}.|n

Progress: Floor {instance.current_floor + 1}/{dungeon['floors']}, {instance.enemies_defeated} enemies defeated

Rewards earned:
{rewards}"""


def _calculate_dungeon_rewards(character, instance: DungeonInstance) -> str:
    """Calculate and give rewards for dungeon progress."""
    dungeon = DUNGEON_DEFINITIONS[instance.dungeon_key]
    drops = dungeon.get("drops", {})
    
    reward_lines = []
    
    # Zeni reward
    zeni_min, zeni_max = drops.get("zeni", (100, 500))
    zeni = random.randint(zeni_min, zeni_max)
    zeni = int(zeni * (instance.current_floor + 1) / dungeon['floors'])
    character.db.zeni = character.db.get('zeni', 0) + zeni
    reward_lines.append(f"  +{zeni} Zeni")
    
    # XP reward
    xp = instance.enemies_defeated * 50
    character.db.xp = character.db.get('xp', 0) + xp
    reward_lines.append(f"  +{xp} XP")
    
    # Special drops based on progress
    if instance.current_floor >= dungeon['floors'] - 1:
        # Completed dungeon!
        for item_key, (min_q, max_q) in drops.items():
            if item_key == "zeni":
                continue
            if random.randint(1, 100) <= 30:
                qty = random.randint(min_q, max_q)
                from world.inventory import add_item
                add_item(character, item_key, qty)
                reward_lines.append(f"  +{item_key} x{qty}")
    
    return "\n".join(reward_lines)


def defeat_enemy_in_dungeon(character, enemy_pl: int) -> tuple[bool, str]:
    """
    Process enemy defeat in dungeon.
    
    Args:
        character: The character
        enemy_pl: Power level of defeated enemy
    
    Returns:
        Tuple of (advanced, message)
    """
    instance = _dungeon_instances.get(character.id)
    if not instance or instance.state != DungeonState.ACTIVE:
        return False, "Not in an active dungeon."
    
    dungeon = DUNGEON_DEFINITIONS[instance.dungeon_key]
    
    # Track defeat
    instance.enemies_defeated += 1
    instance.enemies_on_floor -= 1
    
    # XP for enemy
    xp = int(enemy_pl * 0.5)
    character.db.xp = character.db.get('xp', 0) + xp
    
    # Check if floor complete
    if instance.enemies_on_floor <= 0:
        # Advance to next floor
        instance.current_floor += 1
        character.db.dungeon_floor = instance.current_floor
        
        # Check if dungeon complete
        if instance.current_floor >= dungeon['floors']:
            instance.state = DungeonState.COMPLETED
            return True, _complete_dungeon(character, instance)
        
        # Setup next floor
        instance.enemies_on_floor = dungeon.get("enemies_per_floor", 3)
        floor_info = dungeon["floors"][instance.current_floor]
        
        return True, f"""|g=== FLOOR {instance.current_floor + 1} CLEARED! ===|n

Entering: {floor_info['name']}
{floor_info['description']}

Enemies: {instance.enemies_on_floor}"""
    
    return True, f"Enemy defeated! {instance.enemies_on_floor} remaining on this floor."


def _complete_dungeon(character, instance: DungeonInstance) -> str:
    """Handle dungeon completion."""
    dungeon = DUNGEON_DEFINITIONS[instance.dungeon_key]
    drops = dungeon.get("drops", {})
    
    reward_lines = ["|g=== DUNGEON COMPLETE! ===|n"]
    
    # Bonus zenii
    zeni_bonus = drops.get("zeni_bonus", 0)
    if zeni_bonus:
        character.db.zeni = character.db.get('zeni', 0) + zeni_bonus
        reward_lines.append(f"+{zeni_bonus} Zeni bonus!")
    
    # Grant special rewards
    from world.inventory import add_item
    
    for item_key, (min_q, max_q) in drops.items():
        if item_key in ["zeni", "zeni_bonus", "reputation"]:
            continue
        qty = random.randint(min_q, max_q)
        add_item(character, item_key, qty)
        reward_lines.append(f"+{item_key} x{qty}")
    
    # Faction reputation
    faction = drops.get("reputation")
    if faction:
        from world.guild_system import add_reputation
        add_reputation(character, 100, "completed dungeon")
        reward_lines.append(f"+100 reputation ({faction})")
    
    return "\n".join(reward_lines)


def get_dungeon_status(character) -> str:
    """Get current dungeon status."""
    instance = _dungeon_instances.get(character.id)
    if not instance:
        return "|yYou are not in a dungeon.|n\nUse 'dungeon list' to see available dungeons."
    
    dungeon = DUNGEON_DEFINITIONS[instance.dungeon_key]
    floor_info = dungeon["floors"][instance.current_floor]
    
    lines = [
        f"|g=== {dungeon['name'].upper()} ===|n",
        f"Floor: {instance.current_floor + 1}/{dungeon['floors']}",
        f"{floor_info['name']}",
        f"{floor_info['description']}",
        f"\nEnemies remaining: {instance.enemies_on_floor}",
        f"Total defeated: {instance.enemies_defeated}",
    ]
    
    return "".join(lines)


def get_dungeon_list() -> str:
    """Get list of available dungeons."""
    lines = ["|y=== DUNGEONS ===|n\n"]
    
    for key, dungeon in DUNGEON_DEFINITIONS.items():
        lines.append(f"|b{dungeon['name']}|n")
        lines.append(f"  Theme: {dungeon['theme']}")
        lines.append(f"  Floors: {dungeon['floors']}")
        lines.append(f"  Difficulty: {dungeon['difficulty']}")
        lines.append(f"  Recommended PL: {dungeon['recommended_pl']:,}")
        lines.append(f"  {dungeon['description']}\n")
    
    return "".join(lines)


# =============================================================================
# DUNGEON COMMANDS
# =============================================================================


class DungeonCommand:
    """Dungeon command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """Handle dungeon subcommands."""
        args = args.strip().lower() if args else ""
        
        if not args:
            return get_dungeon_status(caller)
        
        elif args == "list":
            return get_dungeon_list()
        
        elif args.startswith("enter "):
            dungeon_name = args[6:].strip().lower().replace(" ", "_")
            # Find matching dungeon
            matched = None
            for key in DUNGEON_DEFINITIONS:
                if key == dungeon_name or DUNGEON_DEFINITIONS[key]['name'].lower().replace(" ", "_") == dungeon_name:
                    matched = key
                    break
            
            if not matched:
                return "Unknown dungeon. Use 'dungeon list' to see available dungeons."
            
            success, msg = enter_dungeon(caller, matched)
            return msg if success else f"|r{msg}|n"
        
        elif args == "exit":
            success, msg = exit_dungeon(caller)
            return msg if success else f"|r{msg}|n"
        
        elif args == "floor" or args == "progress":
            return get_dungeon_status(caller)
        
        elif args == "status":
            return get_dungeon_status(caller)
        
        else:
            return """|yDungeon Commands:|n
  dungeon list     - Show available dungeons
  dungeon enter <name> - Enter a dungeon
  dungeon exit    - Exit current dungeon
  dungeon floor   - Show floor info
  dungeon status  - Show dungeon status|

Each dungeon has multiple floors with enemies.
Defeat all enemies to advance. Boss on final floor!|
"""
