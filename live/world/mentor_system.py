"""
================================================================================
MENTOR SYSTEM - DBForged Vertical Slice
================================================================================

This module provides a mentor system where players can learn iconic techniques
from master NPCs.

MENTOR SYSTEM:
--------------
Players can seek out masters to learn signature techniques:

MASTERS:
--------
1. Master Roshi (Turtle Hermit)
   - Location: Kame House
   - Techniques: Kamehameha, Turtle Stance
   - Requirements: None

2. King Kai (North Kai)
   - Location: Otherworld
   - Techniques: Kaioken, Spirit Ball, King's Beam
   - Requirements: Complete Kaiō's Test

3. Guru (Namek Elder)
   - Location: Namek
   - Techniques: Potential Unlock, Moonsong
   - Requirements: Reach Namek

4. Elder Kai (Otherworld)
   - Location: Otherworld
   - Techniques: Potential Unlock (Ultimate)
   - Requirements: Complete Elder Kai's Planet

5. Frieza (Emperor)
   - Location: Planet Vegeta
   - Techniques: Death Beam, Death Ball, Nova Strike
   - Requirements: Join Frieza's Army

6. Vegeta (Prince)
   - Location: Various
   - Techniques: Final Flash, Galick Gun
   - Requirements: Saiyan heritage

7. Piccolo (Namekian Warrior)
   - Location: Wastelands
   - Techniques: Special Beam Cannon, Light Grenade
   - Requirements: None (teaches all)

8. Gohan (Ultimate Gohan)
   - Location: Lookout
   - Techniques: Masenko, Potential Unlock
   - Requirements: Reach Lookout

LEARNING:
---------
- Each technique has a learning cost
- Must meet PL requirements
- Must not already know the technique
- Some techniques require quest completion

Example Usage:
-------------
# Find mentors
mentor list

# Learn a technique
learn kamehameha

# Check what you can learn
mentor status
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Any
from enum import Enum


# =============================================================================
# MENTOR DATA
# =============================================================================

class MentorType(Enum):
    """Types of mentors."""
    KAI = "kai"
    SAIYAN = "saiyan"
    NAMEKIAN = "namekian"
    EARTH = "earth"
    FRIEZA = "frieza"


class Mentor:
    """Represents a mentor NPC."""
    
    def __init__(
        self,
        key: str,
        name: str,
        title: str,
        location: str,
        description: str,
        techniques: List[Dict],
        faction: str = None,
        quest: str = None,
        pl_required: int = 0,
    ):
        self.key = key
        self.name = name
        self.title = title
        self.location = location
        self.description = description
        self.techniques = techniques
        self.faction = faction
        self.quest = quest
        self.pl_required = pl_required


# Define all mentors
MENTORS = {
    "roshi": Mentor(
        key="roshi",
        name="Master Roshi",
        title="Turtle Hermit",
        location="kame_island",
        description="The legendary Turtle Hermit. His Kamehameha is world-famous.",
        techniques=[
            {"key": "kamehameha", "name": "Kamehameha", "cost": 1000, "pl_required": 0, "type": "special"},
            {"key": "turtle_stance", "name": "Turtle Stance", "cost": 500, "pl_required": 0, "type": "passive"},
        ],
    ),
    "kingsam": Mentor(
        key="kingsam",
        name="King Kai",
        title="North Kai",
        location="otherworld",
        description="The mischievous North Kai. He teaches the dangerous Kaioken technique.",
        quest="kaios_test",
        techniques=[
            {"key": "kaioken", "name": "Kaioken", "cost": 5000, "pl_required": 15000, "type": "transformation"},
            {"key": "spirit_ball_kai", "name": "Spirit Ball", "cost": 3000, "pl_required": 10000, "type": "special"},
            {"key": "kings_beam", "name": "King's Beam", "cost": 8000, "pl_required": 25000, "type": "special"},
        ],
    ),
    "guru": Mentor(
        key="guru",
        name="Guru",
        title="Namek Elder",
        location="namek",
        description="The wise Elder of Namek. He can unlock latent potential.",
        faction="namekian_clan",
        techniques=[
            {"key": "potential_unlock", "name": "Potential Unlock", "cost": 10000, "pl_required": 20000, "type": "passive"},
            {"key": "moonsong", "name": "Moonsong", "cost": 5000, "pl_required": 15000, "type": "special"},
        ],
    ),
    "elder_kai": Mentor(
        key="elder_kai",
        name="Elder Kai",
        title="Otherworld Elder",
        location="otherworld",
        description="An ancient Kai who can perform the ultimate potential unlock.",
        quest="elder_kai_trial",
        techniques=[
            {"key": "ultimate_unlock", "name": "Ultimate Potential Unlock", "cost": 50000, "pl_required": 75000, "type": "passive"},
        ],
    ),
    "frieza": Mentor(
        key="frieza",
        name="Frieza",
        title="Emperor of the Universe",
        location="planet_vegeta",
        description="The tyrannical Emperor. His techniques are deadly.",
        faction="frieza_army",
        techniques=[
            {"key": "death_beam", "name": "Death Beam", "cost": 8000, "pl_required": 20000, "type": "special"},
            {"key": "death_ball", "name": "Death Ball", "cost": 15000, "pl_required": 40000, "type": "special"},
            {"key": "nova_strike", "name": "Nova Strike", "cost": 20000, "pl_required": 50000, "type": "special"},
        ],
    ),
    "vegeta": Mentor(
        key="vegeta",
        name="Vegeta",
        title="Prince of Saiyans",
        location="various",
        description="The proud Prince of all Saiyans. He'll teach you his signature techniques.",
        techniques=[
            {"key": "final_flash", "name": "Final Flash", "cost": 10000, "pl_required": 25000, "type": "special"},
            {"key": "galick_gun", "name": "Galick Gun", "cost": 8000, "pl_required": 18000, "type": "special"},
        ],
    ),
    "piccolo": Mentor(
        key="piccolo",
        name="Piccolo",
        title="Namekian Warrior",
        location="wastelands",
        description="The reincarnated Namekian. He teaches techniques to any worthy warrior.",
        techniques=[
            {"key": "special_beam_cannon", "name": "Special Beam Cannon", "cost": 12000, "pl_required": 30000, "type": "special"},
            {"key": "light_grenade", "name": "Light Grenade", "cost": 15000, "pl_required": 35000, "type": "special"},
            {"key": "multi_form", "name": "Multi-Form", "cost": 8000, "pl_required": 15000, "type": "special"},
        ],
    ),
    "gohan": Mentor(
        key="gohan",
        name="Gohan",
        title="Ultimate Hybrid",
        location="lookout",
        description="The潜力無盡的孫悟飯 (Gohan). He can help unlock your potential.",
        techniques=[
            {"key": "masenko", "name": "Masenko", "cost": 6000, "pl_required": 12000, "type": "special"},
            {"key": "potential_boost", "name": "Potential Boost", "cost": 8000, "pl_required": 18000, "type": "passive"},
        ],
    ),
    "tenshinhan": Mentor(
        key="tenshinhan",
        name="Tenshinhan",
        title="Three-Eyed Warrior",
        location="ding_rong",
        description="The Crane School disciple turned hero. Teaches the Ki Blade.",
        techniques=[
            {"key": "ki_blade", "name": "Ki Blade", "cost": 4000, "pl_required": 8000, "type": "special"},
            {"key": "solar_flare", "name": "Solar Flare", "cost": 2000, "pl_required": 3000, "type": "special"},
        ],
    ),
    "krillin": Mentor(
        key="krillin",
        name="Krillin",
        title="Earth's Protector",
        location="kame_island",
        description="The loyal human warrior. His techniques are practical.",
        techniques=[
            {"key": "destructo_disc", "name": "Destructo Disc", "cost": 5000, "pl_required": 10000, "type": "special"},
            {"key": "scatter_shot", "name": "Scatter Shot", "cost": 3000, "pl_required": 6000, "type": "special"},
        ],
    ),
}


# =============================================================================
# MENTOR FUNCTIONS
# =============================================================================


def get_available_mentors(character) -> List[Mentor]:
    """
    Get list of mentors available to a character.
    
    Args:
        character: The character seeking a mentor
    
    Returns:
        List of available mentors
    """
    pl = character.db.get('power_level', 0)
    faction = character.db.get('faction')
    completed_quests = character.db.get('completed_quests', [])
    
    available = []
    
    for key, mentor in MENTORS.items():
        # Check PL requirement
        if pl < mentor.pl_required:
            continue
        
        # Check faction requirement
        if mentor.faction and faction != mentor.faction:
            continue
        
        # Check quest requirement
        if mentor.quest and mentor.quest not in completed_quests:
            continue
        
        available.append(mentor)
    
    return available


def get_learnable_techniques(character, mentor_key: str) -> List[Dict]:
    """
    Get techniques a character can learn from a mentor.
    
    Args:
        character: The learning character
        mentor_key: The mentor's key
    
    Returns:
        List of learnable techniques
    """
    if mentor_key not in MENTORS:
        return []
    
    mentor = MENTORS[mentor_key]
    known_techniques = character.db.get('known_techniques', [])
    pl = character.db.get('power_level', 0)
    zeni = character.db.get('zeni', 0)
    
    learnable = []
    
    for tech in mentor.techniques:
        # Skip if already known
        if tech['key'] in known_techniques:
            continue
        
        # Check PL requirement
        if pl < tech['pl_required']:
            continue
        
        # Check cost
        if zeni < tech['cost']:
            continue
        
        learnable.append(tech)
    
    return learnable


def learn_technique(character, technique_key: str) -> tuple[bool, str]:
    """
    Learn a technique from a mentor.
    
    Args:
        character: The learning character
        technique_key: The technique to learn
    
    Returns:
        Tuple of (success, message)
    """
    known_techniques = character.db.get('known_techniques', [])
    
    # Check if already known
    if technique_key in known_techniques:
        return False, "You already know this technique!"
    
    # Find which mentor teaches this
    mentor_found = None
    technique_info = None
    
    for key, mentor in MENTORS.items():
        for tech in mentor.techniques:
            if tech['key'] == technique_key:
                mentor_found = mentor
                technique_info = tech
                break
        if mentor_found:
            break
    
    if not mentor_found:
        return False, "No mentor teaches this technique."
    
    pl = character.db.get('power_level', 0)
    zen = character.db.get('zeni', 0)
    
    # Check PL
    if pl < technique_info['pl_required']:
        return False, f"You need {technique_info['pl_required']:,} PL to learn {technique_info['name']}."
    
    # Check zeni
    if zen < technique_info['cost']:
        return False, f"You need {technique_info['cost']:,} zeni to learn {technique_info['name']}."
    
    # Check faction
    if mentor_found.faction:
        if character.db.get('faction') != mentor_found.faction:
            return False, f"You must be in {mentor_found.faction} to learn from {mentor_found.name}."
    
    # Check quest
    if mentor_found.quest:
        completed = character.db.get('completed_quests', [])
        if mentor_found.quest not in completed:
            return False, f"You must complete {mentor_found.quest} to learn from {mentor_found.name}."
    
    # Learn the technique
    character.db.zeni = zen - technique_info['cost']
    known_techniques.append(technique_key)
    character.db.known_techniques = known_techniques
    
    return True, f"|gYou learned {technique_info['name']} from {mentor_found.name}!|n"


def get_mentor_status(character) -> str:
    """
    Get formatted mentor status.
    
    Args:
        character: The character
    
    Returns:
        Formatted status string
    """
    pl = character.db.get('power_level', 0)
    zen = character.db.get('zeni', 0)
    known = character.db.get('known_techniques', [])
    
    lines = ["|y=== MENTOR SYSTEM ===|n\n"]
    lines.append(f"Your PL: {pl:,} | Your Zeni: {zen:,}\n")
    
    # Show what techniques you know
    lines.append("\n|wTechniques You Know:|n")
    if not known:
        lines.append("  None yet! Seek out a mentor.\n")
    else:
        for tech_key in known:
            lines.append(f"  |g✓|n {tech_key}\n")
    
    # Show available mentors and their techniques
    lines.append("\n|wAvailable Masters:|n")
    
    available = get_available_mentors(character)
    
    if not available:
        lines.append("  No mentors available yet. Increase your PL!\n")
    else:
        for mentor in available:
            learnable = get_learnable_techniques(character, mentor.key)
            
            lines.append(f"\n  |c{mentor.name}|n - {mentor.title}\n")
            lines.append(f"  Location: {mentor.location}\n")
            
            if learnable:
                lines.append("  |gAvailable Techniques:|n")
                for tech in learnable:
                    lines.append(f"    - {tech['name']}: {tech['cost']:,} zeni, {tech['pl_required']:,} PL\n")
            else:
                # Check if any are known but unavailable due to cost/PL
                lines.append("  |xTechniques available:|n")
                for tech in mentor.techniques:
                    if tech['key'] in known:
                        lines.append(f"    - {tech['name']} |g(known)|n\n")
                    elif pl < tech['pl_required']:
                        lines.append(f"    - {tech['name']} |r(need {tech['pl_required']:,} PL)|n\n")
                    elif zen < tech['cost']:
                        lines.append(f"    - {tech['name']} |r(need {tech['cost']:,} zeni)|n\n")
                    else:
                        lines.append(f"    - {tech['name']}: {tech['cost']:,} zeni, {tech['pl_required']:,} PL\n")
    
    return "".join(lines)


def list_mentors(character) -> str:
    """
    List all mentors in the game.
    
    Args:
        character: The character
    
    Returns:
        Formatted list
    """
    pl = character.db.get('power_level', 0)
    zen = character.db.get('zeni', 0)
    
    lines = ["|y=== ALL MASTERS IN THE WORLD ===|n\n"]
    
    for key, mentor in MENTORS.items():
        # Check availability
        available = True
        
        if pl < mentor.pl_required:
            available = False
        if mentor.faction and character.db.get('faction') != mentor.faction:
            available = False
        if mentor.quest and mentor.quest not in character.db.get('completed_quests', []):
            available = False
        
        status = "|gAvailable|n" if available else "|rNot Available|n"
        
        lines.append(f"|c{mentor.name}|n - {mentor.title}\n")
        lines.append(f"  {status}\n")
        lines.append(f"  Location: {mentor.location}\n")
        lines.append(f"  {mentor.description}\n")
        
        if mentor.pl_required > 0:
            lines.append(f"  |yRequires:|n {mentor.pl_required:,} PL\n")
        if mentor.faction:
            lines.append(f"  |yRequires:|n {mentor.faction} faction\n")
        if mentor.quest:
            lines.append(f"  |yRequires:|n {mentor.quest} quest\n")
        
        lines.append("\n")
    
    return "".join(lines)


# =============================================================================
# MENTOR COMMANDS
# =============================================================================


class MentorCommand:
    """Mentor command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """Handle mentor subcommands."""
        args = args.strip().lower() if args else ""
        
        if args == "" or args == "status":
            return get_mentor_status(caller)
        
        if args == "list":
            return list_mentors(caller)
        
        if args.startswith("learn "):
            tech = args[6:].strip().lower().replace(" ", "_")
            success, msg = learn_technique(caller, tech)
            return msg if success else f"|r{msg}|n"
        
        # Show help
        return """|yMentor Commands:|n
  mentor              - Show mentor status
  mentor list        - List all masters
  learn <technique>  - Learn from a mentor

Finding Masters:
  - Master Roshi: Kame Island
  - King Kai: Otherworld (complete Kaiō's Test)
  - Guru: Namek (join Namekian Clan)
  - Frieza: Planet Vegeta (join Frieza's Army)
  - Piccolo: Wastelands
  - And more...

Note: Learn techniques from masters using 'learn <technique>'
"""
