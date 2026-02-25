"""
================================================================================
GUILD/CLAN SYSTEM - DBForged Vertical Slice
================================================================================

This module provides guild/clan functionality for DBZ-themed gameplay.
Players can join factions and compete for territory and resources.

FACTIONS:
--------
1. SAIYAN ARMY - "The Warrior Race"
   - Led by: King Vegeta (NPC)
   - Specialty: Combat power, transformation bonuses
   - Members: Goku, Vegeta, Gohan, Trunks, Bardock
   - Benefits: +20% XP, +10% PL gain in combat

2. CAPSULE CORP - "Technology & Innovation"
   - Led by: Dr. Brief (NPC)
   - Specialty: Ki tech, capsule items
   - Members: Bulma, Trunks (future), Vegeta (sometimes)
   - Benefits: +15% item drop rate, free capsule repairs

3. RED RIBBON ARMY - "Military Precision"
   - Led by: Commander Red (NPC)
   - Specialty: Weapons, scouts
   - Members: General Blue, Captain Ginyu (later)
   - Benefits: +10% Zeni from combat, tracking ability

4. KAME HOUSE - "The Turtle Way"
   - Led by: Master Roshi (NPC)
   - Specialty: Balanced training, techniques
   - Members: Krillin, Yamcha, Tien, Launch
   - Benefits: +15% technique mastery gain

5. NAMEKIAN CLAN - "The Dragon Clan"
   - Led by: Guru (NPC)
   - Specialty: Ki sensing, regeneration
   - Members: Piccolo, Nail, Dende
   - Benefits: +25% KI, +20% regeneration

GUILD FEATURES:
---------------
- Faction membership (one at a time)
- Faction reputation system
- Faction-specific quests
- Faction-only techniques
- Territory control (future)
- Faction wars (future)
- Rank progression

RANKS:
------
- Recruit: Starting rank
- Soldier: After 100 reputation
- Captain: After 500 reputation  
- Commander: After 2000 reputation
- General: After 10000 reputation (faction leader only)

COMMANDS:
---------
- faction join <name> - Join a faction
- faction leave - Leave current faction
- faction info - View faction info
- faction reputation - Check reputation
- faction members - See online members
- faction quests - Available quests
- faction techniques - Learn faction techniques
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class FactionRank(Enum):
    """Faction rank levels."""
    RECRUIT = "recruit"
    SOLDIER = "soldier"
    CAPTAIN = "captain"
    COMMANDER = "commander"
    GENERAL = "general"


# Faction Definitions
FACTION_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "saiyan_army": {
        "name": "Saiyan Army",
        "title": "The Warrior Race",
        "leader": "King Vegeta",
        "color": "|r",
        "description": "Proud warriors from Planet Vegeta. Masters of combat and transformation.",
        "bonus_xp": 20,
        "bonus_pl_combat": 10,
        "colors": ["gold", "orange", "red"],
        "symbol": "🦁",
        "techniques": ["super_saiyan", "super_saiyan_2", "super_saiyan_3", "kiai", "wild_swing"],
        "requirements": {"race": "saiyan", "min_pl": 1000},
    },
    "capsule_corp": {
        "name": "Capsule Corp",
        "title": "Technology & Innovation",
        "leader": "Dr. Brief",
        "color": "|b",
        "description": "Earth's greatest technology company. Masters of ki devices and capsules.",
        "bonus_item_drop": 15,
        "colors": ["blue", "silver", "white"],
        "symbol": "🟦",
        "techniques": ["scout_scouter", "capsule_repair", "tech_shield"],
        "requirements": {"min_pl": 500},
    },
    "red_ribbon_army": {
        "name": "Red Ribbon Army",
        "title": "Military Precision",
        "leader": "Commander Red",
        "color": "|r",
        "description": "A ruthless military organization seeking world domination.",
        "bonus_zeni": 10,
        "colors": ["red", "black", "silver"],
        "symbol": "⭐",
        "techniques": ["gun_attack", "sniper_shot", "tracking_sense"],
        "requirements": {"min_pl": 500},
    },
    "kame_house": {
        "name": "Kame House",
        "title": "The Turtle Way",
        "leader": "Master Roshi",
        "color": "|g",
        "description": "The way of the Turtle Hermit. Balanced combat and technique mastery.",
        "bonus_technique_mastery": 15,
        "colors": ["green", "brown", "orange"],
        "symbol": "🐢",
        "techniques": ["kamehameha", "solar_flare", "afterimage", "drunken_fist"],
        "requirements": {"min_pl": 100},
    },
    "namekian_clan": {
        "name": "Namekian Clan",
        "title": "The Dragon Clan",
        "leader": "Guru",
        "color": "|c",
        "description": "Mysterious Namekian warriors. Masters of ki sensing and regeneration.",
        "bonus_ki": 25,
        "bonus_regen": 20,
        "colors": ["cyan", "purple", "blue"],
        "symbol": "🐉",
        "techniques": ["regeneration", "namekian_fusion", "eye_beam", "cloning"],
        "requirements": {"race": "namekian", "min_pl": 1000},
    },
}


# Rank thresholds
RANK_REPUTATION = {
    FactionRank.RECRUIT: 0,
    FactionRank.SOLDIER: 100,
    FactionRank.CAPTAIN: 500,
    FactionRank.COMMANDER: 2000,
    FactionRank.GENERAL: 10000,
}


# Reputation gains
REPUTATION_GAINS = {
    "boss_kill": 50,
    "quest_complete": 25,
    "pvp_win": 15,
    "training_session": 5,
    "faction_quest": 100,
    "territory_capture": 500,
}


def join_faction(character, faction_key: str) -> tuple[bool, str]:
    """
    Join a faction.
    
    Args:
        character: The character joining
        faction_key: The faction to join
    
    Returns:
        Tuple of (success, message)
    """
    faction_key = faction_key.lower().replace(" ", "_")
    
    if faction_key not in FACTION_DEFINITIONS:
        return False, "Unknown faction. Use 'faction list' to see available factions."
    
    # Check if already in a faction
    if character.db.faction:
        return False, f"You are already in {character.db.faction}. Leave first."
    
    faction = FACTION_DEFINITIONS[faction_key]
    requirements = faction.get("requirements", {})
    
    # Check requirements
    if "min_pl" in requirements:
        pl = character.db.get('power_level', 0)
        if pl < requirements["min_pl"]:
            return False, f"You need at least {requirements['min_pl']} PL to join {faction['name']}."
    
    if "race" in requirements:
        race = character.db.get('race', 'human')
        if race != requirements["race"]:
            return False, f"Only {requirements['race'].title()}s can join {faction['name']}."
    
    # Join faction
    character.db.faction = faction_key
    character.db.faction_reputation = 0
    character.db.faction_rank = FactionRank.RECRUIT.value
    
    return True, f"|{faction['color']}Welcome to {faction['name']}!|n\n{faction['description']}"


def leave_faction(character) -> tuple[bool, str]:
    """
    Leave current faction.
    
    Args:
        character: The character leaving
    
    Returns:
        Tuple of (success, message)
    """
    if not character.db.faction:
        return False, "You are not in a faction."
    
    faction_key = character.db.faction
    faction = FACTION_DEFINITIONS.get(faction_key, {})
    
    # Clear faction data
    character.db.faction = None
    character.db.faction_reputation = 0
    character.db.faction_rank = None
    
    return True, f"You have left {faction.get('name', faction_key)}."


def get_faction_info(character) -> str:
    """
    Get formatted faction information.
    
    Args:
        character: The character
    
    Returns:
        Formatted faction info
    """
    faction_key = character.db.get('faction')
    if not faction_key:
        return "|yYou are not in a faction.|n\n|yUse 'faction list' to see available factions, then 'faction join <name>' to join.|n"
    
    faction = FACTION_DEFINITIONS.get(faction_key, {})
    reputation = character.db.get('faction_reputation', 0)
    rank = character.db.get('faction_rank', FactionRank.RECRUIT.value)
    
    # Calculate next rank
    next_rank = None
    for r, threshold in sorted(RANK_REPUTATION.items(), key=lambda x: x[1]):
        if threshold > reputation:
            next_rank = (r, threshold)
            break
    
    lines = [
        f"|{faction['color']}=== {faction['name']} ===|n",
        f"{faction['description']}",
        f"\n|yLeader:|n {faction['leader']}",
        f"\n|yRank:|n {rank.title()} ({reputation} reputation)",
    ]
    
    if next_rank:
        needed = next_rank[1] - reputation
        lines.append(f"\n|yNext Rank:|n {next_rank[0].title()} (need {needed} more)")
    
    # Show bonuses
    lines.append(f"\n|yFaction Bonuses:|n")
    if faction.get("bonus_xp"):
        lines.append(f"  +{faction['bonus_xp']}% XP gain")
    if faction.get("bonus_pl_combat"):
        lines.append(f"  +{faction['bonus_pl_combat']}% PL gain in combat")
    if faction.get("bonus_item_drop"):
        lines.append(f"  +{faction['bonus_item_drop']}% item drop rate")
    if faction.get("bonus_zeni"):
        lines.append(f"  +{faction['bonus_zeni']}% Zeni from combat")
    if faction.get("bonus_technique_mastery"):
        lines.append(f"  +{faction['bonus_technique_mastery']}% technique mastery")
    if faction.get("bonus_ki"):
        lines.append(f"  +{faction['bonus_ki']}% max KI")
    if faction.get("bonus_regen"):
        lines.append(f"  +{faction['bonus_regen']}% regeneration")
    
    # Show available techniques
    techniques = faction.get("techniques", [])
    if techniques:
        lines.append(f"\n|yAvailable Techniques:|n")
        for tech in techniques:
            lines.append(f"  - {tech}")
    
    return "".join(lines)


def get_faction_list() -> str:
    """Get list of all factions."""
    lines = ["|y=== FACTIONS ===|n\n"]
    
    for key, faction in FACTION_DEFINITIONS.items():
        lines.append(f"|{faction['color']}{faction['name']}|n - {faction['title']}")
        lines.append(f"  Leader: {faction['leader']}")
        lines.append(f"  {faction['description']}")
        
        # Show requirements
        reqs = faction.get("requirements", {})
        if reqs:
            req_strs = []
            if "min_pl" in reqs:
                req_strs.append(f"Min PL: {reqs['min_pl']:,}")
            if "race" in reqs:
                req_strs.append(f"Race: {reqs['race'].title()}")
            lines.append(f"  Requirements: {', '.join(req_strs)}")
        
        lines.append("")
    
    return "".join(lines)


def add_reputation(character, amount: int, reason: str = "") -> int:
    """
    Add reputation to a character.
    
    Args:
        character: The character
        amount: Reputation to add
        reason: Optional reason for tracking
    
    Returns:
        New reputation total
    """
    if not character.db.faction:
        return 0
    
    current = character.db.get('faction_reputation', 0)
    new = current + amount
    character.db.faction_reputation = new
    
    # Check for rank up
    old_rank = character.db.get('faction_rank', FactionRank.RECRUIT.value)
    new_rank = old_rank
    
    for rank, threshold in RANK_REPUTATION.items():
        if new >= threshold:
            new_rank = rank.value
    
    if new_rank != old_rank:
        character.db.faction_rank = new_rank
        character.msg(f"|g=== FACTION RANK UP! ===|nYou are now a {new_rank.title()}!|n")
    
    return new


def get_faction_bonus(character, bonus_type: str) -> float:
    """
    Get bonus from faction.
    
    Args:
        character: The character
        bonus_type: The bonus type
    
    Returns:
        Bonus value (0 = no bonus)
    """
    faction_key = character.db.get('faction')
    if not faction_key:
        return 0
    
    faction = FACTION_DEFINITIONS.get(faction_key, {})
    
    bonus_map = {
        "xp": faction.get("bonus_xp", 0),
        "pl_combat": faction.get("bonus_pl_combat", 0),
        "item_drop": faction.get("bonus_item_drop", 0),
        "zeni": faction.get("bonus_zeni", 0),
        "technique_mastery": faction.get("bonus_technique_mastery", 0),
        "ki": faction.get("bonus_ki", 0),
        "regen": faction.get("bonus_regen", 0),
    }
    
    return bonus_map.get(bonus_type, 0)


# =============================================================================
# FACTION COMMANDS
# =============================================================================


class FactionCommand:
    """Faction command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """
        Handle faction subcommands.
        
        Args:
            caller: The character using the command
            args: Arguments after "faction "
        
        Returns:
            Result message
        """
        args = args.strip().lower() if args else ""
        
        if not args:
            # Show faction info
            return get_faction_info(caller)
        
        elif args == "list":
            return get_faction_list()
        
        elif args.startswith("join "):
            faction_name = args[5:].strip()
            success, msg = join_faction(caller, faction_name)
            return msg if success else f"|r{msg}|n"
        
        elif args == "leave":
            success, msg = leave_faction(caller)
            return msg if success else f"|r{msg}|n"
        
        elif args == "info":
            return get_faction_info(caller)
        
        elif args == "reputation":
            rep = caller.db.get('faction_reputation', 0)
            rank = caller.db.get('faction_rank', 'recruit')
            return f"|yReputation:|n {rep}\n|yRank:|n {rank.title()}"
        
        elif args == "techniques":
            faction_key = caller.db.get('faction')
            if not faction_key:
                return "|rYou are not in a faction.|n"
            faction = FACTION_DEFINITIONS.get(faction_key, {})
            techniques = faction.get("techniques", [])
            if techniques:
                lines = [f"|yAvailable {faction['name']} Techniques:|n"]
                for tech in techniques:
                    lines.append(f"  - {tech}")
                return "".join(lines)
            return "No techniques available."
        
        else:
            return """|yFaction Commands:|n
  faction list     - See all factions
  faction join <name> - Join a faction
  faction leave   - Leave your faction
  faction info    - View your faction
  faction reputation - Check your reputation
  faction techniques - See available techniques|
"""


# Faction reputation rewards
def on_boss_kill(character, boss_name: str):
    """Award reputation for killing a boss."""
    return add_reputation(character, REPUTATION_GAINS["boss_kill"], f"killed {boss_name}")


def on_quest_complete(character):
    """Award reputation for completing a quest."""
    return add_reputation(character, REPUTATION_GAINS["quest_complete"], "completed quest")


def on_pvp_win(character):
    """Award reputation for winning PvP."""
    return add_reputation(character, REPUTATION_GAINS["pvp_win"], "won PvP")


def on_training_session(character):
    """Award reputation for training."""
    return add_reputation(character, REPUTATION_GAINS["training_session"], "trained")
