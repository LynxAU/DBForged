"""
================================================================================
WORLD BOSS SYSTEM - DBForged Vertical Slice
================================================================================

This module provides World Boss events for DBZ-themed multiplayer gameplay.
Players can team up to fight powerful bosses like Frieza, Cell, and Buu.

WORLD BOSSES:
-------------
1. Frieza (Tier 1) - "The Cold-Blooded Emperor"
   - Power Level: 10,000,000 (Final Form)
   - Abilities: Death Beam, Death Ball, Supernova
   - Weakness: Tired after 5 minutes
   - Drops: Super Senzu, Elite weighted clothing, Saiyan DNA

2. Cell (Tier 2) - "The Perfect Lifeform"
   - Power Level: 25,000,000 (Perfect Form)
   - Abilities: Kamehameha, Solar Flare, Regeneration
   - Weakness: Takes extra damage when interrupted during regeneration
   - Drops: Super Senzu, Ki Amplifier, Namekian Crystal

3. Majin Buu (Tier 3) - "The Innocently Evil"
   - Power Level: 50,000,000 (Super Buu)
   - Abilities: Candy Beam, Planet Burst, Absorption
   - Weakness: Becomes weaker when allies are absorbed
   - Drops: Everything, HP/KI Elixirs, Mega Pod

BOSS MECHANICS:
---------------
1. SPAWNING:
   - Bosses spawn at random times (configurable)
   - Announced to all players globally
   - Boss appears in a specific location

2. PHASES:
   - Each boss has multiple phases
   - HP thresholds trigger new abilities
   - Visual changes between phases

3. COOPERATIVE FIGHTING:
   - Boss targets random player
   - Damage is shared among attackers
   - Players must coordinate to win

4. REWARDS:
   - Based on damage contribution
   - Bonus for final blow
   - Participation reward for all who attacked

BOSS COMMANDS:
---------------
- boss info - Show current/next boss info
- boss attack - Join the fight
- boss status - Show boss HP
- boss reward - Claim your rewards

BOSS TIMERS:
------------
- Boss appears every 2 hours (configurable)
- Boss fight lasts 15 minutes
- 30 minute cooldown between bosses
"""

from __future__ import annotations

import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class BossTier(Enum):
    """Boss difficulty tiers."""
    TIER1 = 1  # Frieza
    TIER2 = 2  # Cell
    TIER3 = 3  # Buu


class BossState(Enum):
    """Boss spawn state."""
    INACTIVE = "inactive"
    ANNOUNCED = "announced"
    ACTIVE = "active"
    DEFEATED = "defeated"


# Boss Definitions
BOSS_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "frieza": {
        "name": "Lord Frieza",
        "tier": BossTier.TIER1,
        "power_level": 10000000,
        "hp": 5000000,
        "description": "The cold-blooded emperor of the universe has arrived!",
        "abilities": ["death_beam", "death_ball", "supernova", "tail_attack"],
        "phases": [
            {"name": "First Form", "hp_percent": 100, "abilities": ["tail_attack"]},
            {"name": "Second Form", "hp_percent": 75, "abilities": ["death_beam"]},
            {"name": "Third Form", "hp_percent": 50, "abilities": ["death_beam", "death_ball"]},
            {"name": "Final Form", "hp_percent": 25, "abilities": ["death_beam", "death_ball", "supernova"]},
        ],
        "weakness": "Tired after 5 minutes (damage taken +50%)",
        "spawn_messages": [
            "A chilling aura spreads across the universe...",
            "Lord Frieza has appeared!",
            "The Emperor has arrived to claim Earth!",
        ],
        "drops": {
            "zeni": (5000, 15000),
            "senzu_bean": (2, 5),
            "super_senzu": (1, 2),
            "weighted_clothing_elite": (1, 1),
            "saiyan_dna": (1, 3),
        },
        "location": "Space",  # Special handling
    },
    "cell": {
        "name": "Perfect Cell",
        "tier": BossTier.TIER2,
        "power_level": 25000000,
        "hp": 10000000,
        "description": "The perfect creation of Dr. Gero has achieved its final form!",
        "abilities": ["kamehameha", "solar_flare", "regeneration", "absorb"],
        "phases": [
            {"name": "Semi-Perfect", "hp_percent": 100, "abilities": ["absorb"]},
            {"name": "Imperfect", "hp_percent": 75, "abilities": ["kamehameha", "solar_flare"]},
            {"name": "Perfect", "hp_percent": 50, "abilities": ["kamehameha", "solar_flare", "regeneration"]},
            {"name": "Perfect (Enraged)", "hp_percent": 25, "abilities": ["kamehameha", "solar_flare", "regeneration", "super_kamehameha"]},
        ],
        "weakness": "Extra damage when interrupted during regeneration",
        "spawn_messages": [
            "A terrifying aura emanates from the lab...",
            "Perfect Cell has awakened!",
            "The ultimate bio-weapon has been completed!",
        ],
        "drops": {
            "zeni": (10000, 25000),
            "senzu_bean": (3, 6),
            "super_senzu": (1, 3),
            "power_bracelet": (1, 1),
            "ki_amplifier": (1, 1),
            "namekian_crystal": (2, 5),
        },
        "location": "West City",
    },
    "buu": {
        "name": "Super Majin Buu",
        "tier": BossTier.TIER3,
        "power_level": 50000000,
        "hp": 25000000,
        "description": "The innocent but deadly Majin Buu has turned super!",
        "abilities": ["candy_beam", "planet_burst", "absorption", "rage_sphere"],
        "phases": [
            {"name": "Super Buu", "hp_percent": 100, "abilities": ["candy_beam", "rage_sphere"]},
            {"name": "Super Buu (Angry)", "hp_percent": 75, "abilities": ["candy_beam", "absorption", "rage_sphere"]},
            {"name": "Super Buu (Evil)", "hp_percent": 50, "abilities": ["candy_beam", "absorption", "planet_burst"]},
            {"name": "Kid Buu", "hp_percent": 25, "abilities": ["candy_beam", "planet_burst", "rage_sphere", "annihilation"]},
        ],
        "weakness": "Weaker when allies are absorbed",
        "spawn_messages": [
            "A massive wave of destructive energy erupts!",
            "Super Buu has appeared!",
            "The most dangerous entity in the universe has awakened!",
        ],
        "drops": {
            "zeni": (20000, 50000),
            "senzu_bean": (5, 10),
            "super_senzu": (2, 5),
            "weighted_clothing_elite": (1, 2),
            "saiyan_dna": (3, 5),
            "elixir_hp": (1, 2),
            "elixir_ki": (1, 2),
            "mega_pod": (1, 1),
        },
        "location": "Earth",
    },
}


@dataclass
class ActiveBoss:
    """
    Represents an active world boss encounter.
    
    Attributes:
        boss_key: Key identifier (frieza, cell, buu)
        current_hp: Current HP remaining
        max_hp: Maximum HP
        phase: Current phase name
        state: Current boss state
        location: Current location
        attackers: Dict of attacker_id -> damage_dealt
        start_time: When boss spawned
        last_action: Last boss action time
        phase_hp_threshold: Next phase HP threshold
    """
    boss_key: str
    current_hp: int
    max_hp: int
    phase: str = "First Form"
    state: BossState = BossState.ACTIVE
    location: str = ""
    attackers: Dict[int, int] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    last_action: float = field(default_factory=time.time)
    phase_hp_threshold: float = 0.75


# Global boss state
_boss_instance: Optional[ActiveBoss] = None
_boss_cooldown_until: float = 0
_last_boss_type: str = ""


# =============================================================================
# BOSS MANAGEMENT
# =============================================================================


def is_boss_active() -> bool:
    """Check if a boss is currently active."""
    global _boss_instance
    return _boss_instance is not None and _boss_instance.state == BossState.ACTIVE


def get_active_boss() -> Optional[ActiveBoss]:
    """Get the active boss instance."""
    return _boss_instance


def spawn_boss(boss_key: str, location: str = "") -> tuple[bool, str]:
    """
    Spawn a world boss.
    
    Args:
        boss_key: The boss to spawn (frieza, cell, buu)
        location: Optional location override
    
    Returns:
        Tuple of (success, message)
    """
    global _boss_instance, _boss_cooldown_until, _last_boss_type
    
    if is_boss_active():
        return False, "A boss is already active!"
    
    if time.time() < _boss_cooldown_until:
        remaining = int(_boss_cooldown_until - time.time())
        return False, f"Boss cooldown: {remaining} seconds remaining."
    
    if boss_key not in BOSS_DEFINITIONS:
        return False, f"Unknown boss: {boss_key}"
    
    boss_def = BOSS_DEFINITIONS[boss_key]
    
    # Create boss instance
    _boss_instance = ActiveBoss(
        boss_key=boss_key,
        current_hp=boss_def["hp"],
        max_hp=boss_def["hp"],
        phase=boss_def["phases"][0]["name"],
        state=BossState.ACTIVE,
        location=location or boss_def.get("location", "Random"),
    )
    
    _last_boss_type = boss_key
    
    return True, f"Boss {boss_def['name']} has spawned!"


def boss_attack(boss: ActiveBoss, target_id: int) -> str:
    """
    Boss attacks a player.
    
    Args:
        boss: The active boss
        target_id: ID of target player
    
    Returns:
        Attack message
    """
    from evennia.objects.models import ObjectDB
    
    target = ObjectDB.objects.filter(id=target_id).first()
    if not target:
        return ""
    
    boss_def = BOSS_DEFINITIONS[boss.boss_key]
    
    # Get current phase abilities
    phase_info = None
    for phase in boss_def["phases"]:
        if boss.current_hp / boss.max_hp <= phase["hp_percent"]:
            phase_info = phase
            break
    
    if not phase_info:
        phase_info = boss_def["phases"][-1]
    
    abilities = phase_info.get("abilities", [])
    ability = random.choice(abilities) if abilities else "attack"
    
    # Calculate damage based on boss PL vs target PL
    target_pl = getattr(target, 'db', {}).get('power_level', 100)
    damage = int(boss_def["power_level"] * 0.1)  # 10% of boss PL
    
    # Scale damage based on PL difference
    if target_pl > boss_def["power_level"]:
        damage = int(damage * 0.5)
    else:
        ratio = target_pl / boss_def["power_level"]
        damage = int(damage * (1 + ratio))
    
    # Apply damage
    current_hp = getattr(target, 'db', {}).get('hp', 100)
    new_hp = max(0, current_hp - damage)
    target.db.hp = new_hp
    
    # Message
    ability_names = {
        "death_beam": "fires a Death Beam",
        "death_ball": "unleashes a Death Ball",
        "supernova": "launches a massive Supernova",
        "tail_attack": "swings their tail",
        "kamehameha": "fires a Kamehameha",
        "solar_flare": "uses Solar Flare!",
        "regeneration": "begins regenerating!",
        "absorb": "attempts to absorb energy!",
        "candy_beam": "fires Candy Beam!",
        "planet_burst": "charges Planet Burst!",
        "rage_sphere": "creates a massive energy sphere!",
        "annihilation": "prepares total annihilation!",
        "super_kamehameha": "unleashes Super Kamehameha!",
    }
    
    action = ability_names.get(ability, "attacks")
    msg = f"|r{boss_def['name']} {action} at {target.name} for {damage} damage!|n"
    
    # Check if target died
    if new_hp <= 0:
        msg += f"\n|r{target.name} has been defeated!|n"
    
    return msg


def deal_damage_to_boss(attacker_id: int, damage: int) -> tuple[bool, str]:
    """
    Deal damage to the active boss.
    
    Args:
        attacker_id: ID of attacking player
        damage: Damage amount
    
    Returns:
        Tuple of (hit_boss, message)
    """
    global _boss_instance
    
    if not is_boss_active():
        return False, "No boss is active."
    
    boss = _boss_instance
    boss_def = BOSS_DEFINITIONS[boss.boss_key]
    
    # Track damage
    if attacker_id not in boss.attackers:
        boss.attackers[attacker_id] = 0
    boss.attackers[attacker_id] += damage
    
    # Apply damage
    boss.current_hp -= damage
    
    # Check phase transition
    hp_percent = boss.current_hp / boss.max_hp
    for phase in boss_def["phases"]:
        if hp_percent <= phase["hp_percent"]:
            if boss.phase != phase["name"]:
                boss.phase = phase["name"]
                return True, f"|y{boss_def['name']} enters {phase['name']}!|n"
    
    # Check for defeat
    if boss.current_hp <= 0:
        return True, "defeat"
    
    return True, ""


def defeat_boss(killer_id: int) -> str:
    """
    Handle boss defeat.
    
    Args:
        killer_id: ID of player who got final blow
    
    Returns:
        Victory message
    """
    global _boss_instance, _boss_cooldown_until
    
    if not _boss_instance:
        return "No boss to defeat."
    
    boss = _boss_instance
    boss_def = BOSS_DEFINITIONS[boss.boss_key]
    
    # Calculate rewards for each attacker
    from evennia.objects.models import ObjectDB
    
    reward_messages = []
    
    for attacker_id, damage in boss.attackers.items():
        attacker = ObjectDB.objects.filter(id=attacker_id).first()
        if not attacker:
            continue
        
        # Damage contribution percentage
        contribution = damage / boss.max_hp
        if contribution < 0.01:
            continue  # Too small to reward
        
        # Calculate rewards
        from world.inventory import add_item
        import random
        
        rewards = []
        
        # Base reward based on contribution
        zeni_min = int(boss_def["drops"]["zeni"][0] * contribution)
        zeni_max = int(boss_def["drops"]["zeni"][1] * contribution)
        zeni = random.randint(zeni_min, zeni_max)
        attacker.db.zeni = attacker.db.get('zeni', 0) + zeni
        rewards.append(f"{zeni} Zeni")
        
        # Item drops (random chance based on contribution)
        for item_key, (min_qty, max_qty) in boss_def["drops"].items():
            if item_key == "zeni":
                continue
            
            # Higher contribution = higher drop chance
            drop_chance = contribution * 100
            if random.randint(1, 100) <= drop_chance:
                qty = random.randint(min_qty, max_qty)
                add_item(attacker, item_key, qty)
                from world.inventory import ITEM_DEFINITIONS
                item_name = ITEM_DEFINITIONS.get(item_key, {}).get("name", item_key)
                rewards.append(f"{item_name} x{qty}")
        
        # Bonus for final blow
        if attacker_id == killer_id:
            rewards.append("FINAL BLOW BONUS!")
        
        reward_msg = f"|g{attacker.name} received: {', '.join(rewards)}|n"
        attacker.msg(reward_msg)
        reward_messages.append(reward_msg)
    
    # Announce defeat
    msg = f"|y=== BOSS DEFEATED ===|n"
    msg += f"|y{boss_def['name']} has been defeated!|n"
    msg += f"|yAll participants have been rewarded!|n"
    
    # Clear boss
    _boss_instance = None
    _boss_cooldown_until = time.time() + 1800  # 30 minute cooldown
    
    return msg


def get_boss_status() -> str:
    """Get formatted boss status."""
    if not is_boss_active():
        return "|rNo boss is currently active.|n"
    
    boss = _boss_instance
    boss_def = BOSS_DEFINITIONS[boss.boss_key]
    
    hp_percent = (boss.current_hp / boss.max_hp) * 100
    attacker_count = len(boss.attackers)
    
    lines = [
        f"|y=== WORLD BOSS: {boss_def['name']} ===|n",
        f"Phase: {boss.phase}",
        f"HP: {boss.current_hp:,} / {boss.max_hp:,} ({hp_percent:.1f}%)",
        f"Attackers: {attacker_count}",
        f"Weakness: {boss_def['weakness']}",
    ]
    
    return "".join(lines)


# Boss spawning configuration
BOSS_SPAWN_INTERVAL = 7200  # 2 hours in seconds
BOSS_DURATION = 900  # 15 minutes
BOSS_COOLDOWN = 1800  # 30 minutes


def auto_spawn_boss() -> tuple[bool, str]:
    """
    Automatically spawn a boss based on schedule.
    
    Returns:
        Tuple of (spawned, message)
    """
    global _boss_cooldown_until, _last_boss_type
    
    # Check cooldown
    if time.time() < _boss_cooldown_until:
        return False, "Boss cooldown active."
    
    # Determine boss tier (rotate through them)
    boss_tiers = {
        1: "frieza",
        2: "cell",
        3: "buu",
    }
    
    # Round-robin through bosses
    used_bosses = []
    if _last_boss_type:
        current_tier = list(BOSS_DEFINITIONS.keys()).index(_last_boss_type) + 1
    else:
        current_tier = 0
    
    # Pick next boss
    next_tier = (current_tier % 3) + 1
    boss_key = boss_tiers[next_tier]
    
    return spawn_boss(boss_key)


# =============================================================================
# BOSS COMMANDS
# =============================================================================


class BossCommand:
    """Boss command handler for db_commands.py integration."""
    
    @staticmethod
    def handle(caller, args: str) -> str:
        """
        Handle boss subcommands.
        
        Args:
            caller: The character using the command
            args: Arguments after "boss "
        
        Returns:
            Result message
        """
        args = args.strip().lower() if args else ""
        
        if not args:
            # Show boss info
            return get_boss_status()
        
        elif args == "info":
            return get_boss_status()
        
        elif args == "status":
            return get_boss_status()
        
        elif args == "attack" or args == "join":
            # Join the fight
            if not is_boss_active():
                return "No boss is active right now."
            
            boss = _boss_instance
            boss_def = BOSS_DEFINITIONS[boss.boss_key]
            
            # Add attacker to list
            if caller.id not in boss.attackers:
                boss.attackers[caller.id] = 0
            
            return f"|gYou join the fight against {boss_def['name']}!|n"
        
        elif args.startswith("damage "):
            # Debug command to damage boss
            if not is_boss_active():
                return "No boss is active."
            
            try:
                damage = int(args.split()[1])
            except (ValueError, IndexError):
                return "Usage: boss damage <amount>"
            
            hit, msg = deal_damage_to_boss(caller.id, damage)
            if msg == "defeat":
                return defeat_boss(caller.id)
            elif hit:
                return f"You deal {damage} damage to the boss!\n{msg}"
            return msg
        
        elif args == "spawn" and caller.check_permstring("admin"):
            # Admin spawn
            boss_key = "buu"  # Default
            success, msg = spawn_boss(boss_key)
            return msg
        
        elif args == "list":
            # List available bosses
            lines = ["|y=== Available World Bosses ===|n"]
            for key, boss in BOSS_DEFINITIONS.items():
                lines.append(f"\n|b{boss['name']}|n (Tier {boss['tier'].value})")
                lines.append(f"  PL: {boss['power_level']:,}")
                lines.append(f"  {boss['description']}")
                lines.append(f"  Weakness: {boss['weakness']}")
            return "".join(lines)
        
        else:
            return """|yBoss Commands:|n
  boss           - Show boss status
  boss info      - Show boss status  
  boss attack    - Join the fight
  boss list      - List available bosses|
"""


def announce_boss_spawn():
    """Announce boss spawn to all players."""
    if not is_boss_active():
        return ""
    
    boss = _boss_instance
    boss_def = BOSS_DEFINITIONS[boss.boss_key]
    
    lines = ["|r!!! WORLD BOSS APPEARS !!!|n"]
    lines.append(f"|r{boss_def['name']} has appeared!|n")
    lines.append(f"|y{boss_def['description']}|n")
    lines.append(f"Type |wboss attack|n to join the fight!")
    
    return "".join(lines)
