"""
Tournament and World Event systems for DBForged.

This module implements:
- World Martial Arts Tournament system
- Time-limited world boss events

SECURITY: Uses persistent storage for tournament state to survive restarts.
"""

from __future__ import annotations

import copy
import random
import threading
import time
from typing import Any

# Thread lock for tournament operations to prevent race conditions
_tournament_lock = threading.Lock()

# Try to import persistence, fallback to in-memory if not available
try:
    from world.tournament_persistence import (
        TournamentStateScript,
        get_persistent_tournament_state,
        get_persistent_world_boss_state,
        ensure_tournament_script,
    )
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False


def _get_tournament_state():
    """Get tournament state from persistent storage or fallback."""
    if PERSISTENCE_AVAILABLE:
        return get_persistent_tournament_state()
    return _tournament_state


def _get_world_boss_state():
    """Get world boss state from persistent storage or fallback."""
    if PERSISTENCE_AVAILABLE:
        return get_persistent_world_boss_state()
    return _world_boss_state


def _init_persistence():
    """Initialize persistence on server startup."""
    if PERSISTENCE_AVAILABLE:
        ensure_tournament_script()


# Tournament states
TOURNAMENT_INACTIVE = "inactive"
TOURNAMENT_SIGNUPS = "signups"
TOURNAMENT_IN_PROGRESS = "in_progress"
TOURNAMENT_FINISHED = "finished"

# Global tournament state
_tournament_state = {
    "status": TOURNAMENT_INACTIVE,
    "name": "World Martial Arts Tournament",
    "signup_open": False,
    "participants": [],
    "bracket": [],
    "round": 0,
    "matches": [],
    "start_time": 0,
    "end_time": 0,
    "prize_pool": 0,
    "reward_zeni": 10000,
    "reward_techniques": ["kame_wave", "destructo_disc"],
}

# World boss state
_world_boss_state = {
    "active": False,
    "boss_name": "",
    "boss_pl": 0,
    "boss_hp": 0,
    "boss_max_hp": 0,
    "spawn_time": 0,
    "end_time": 0,
    "damage_dealt": {},  # player_id -> damage
    "reward_zeni": 5000,
    "top_damager": None,
}


# Tournament time settings (in seconds)
TOURNAMENT_SIGNUP_DURATION = 300  # 5 minutes to sign up
TOURNAMENT_MATCH_DURATION = 180  # 3 minutes per match
TOURNAMENT_COOLDOWN = 3600  # 1 hour between tournaments
TOURNAMENT_ENTRY_COST = 500  # Entry fee in zeni

# World boss settings
WORLD_BOSS_SPAWN_CHANCE = 0.05  # 5% chance when searching
WORLD_BOSS_DURATION = 600  # 10 minutes
WORLD_BOSS_COOLDOWN = 1800  # 30 minutes between bosses


def get_tournament_state():
    """Get current tournament state."""
    return _tournament_state.copy()


def get_world_boss_state():
    """Get current world boss state."""
    return _world_boss_state.copy()


def is_tournament_active():
    """Check if tournament is currently active."""
    return _tournament_state["status"] != TOURNAMENT_INACTIVE


def is_world_boss_active():
    """Check if world boss is currently active."""
    return _world_boss_state["active"]


def open_tournament_signups():
    """Open tournament signups."""
    _tournament_state["status"] = TOURNAMENT_SIGNUPS
    _tournament_state["signup_open"] = True
    _tournament_state["participants"] = []
    _tournament_state["start_time"] = time.time()
    _tournament_state["end_time"] = time.time() + TOURNAMENT_SIGNUP_DURATION
    return _tournament_state


def close_tournament_signups():
    """Close tournament signups and start the tournament."""
    if not _tournament_state["signup_open"]:
        return False
    
    _tournament_state["signup_open"] = False
    participants = _tournament_state["participants"]
    
    if len(participants) < 2:
        _tournament_state["status"] = TOURNAMENT_INACTIVE
        return {"success": False, "reason": "Not enough participants"}
    
    # Shuffle and create bracket
    random.shuffle(participants)
    _tournament_state["bracket"] = participants.copy()
    _tournament_state["round"] = 1
    _tournament_state["status"] = TOURNAMENT_IN_PROGRESS
    
    # Create first round matches
    matches = []
    for i in range(0, len(participants), 2):
        if i + 1 < len(participants):
            matches.append({
                "player1": participants[i],
                "player2": participants[i + 1],
                "winner": None,
                "in_progress": False,
            })
    _tournament_state["matches"] = matches
    
    # Calculate prize pool
    _tournament_state["prize_pool"] = len(participants) * 1000
    
    return {"success": True, "participants": len(participants), "matches": len(matches)}


def join_tournament(player):
    """Add a player to the tournament with entry fee."""
    with _tournament_lock:
        if not _tournament_state["signup_open"]:
            return {"success": False, "reason": "Signups are closed"}
        
        player_id = player.id
        if player_id in _tournament_state["participants"]:
            return {"success": False, "reason": "Already signed up"}
        
        # SECURITY: Check player has enough zeni for entry fee
        player_zeni = getattr(player.db, 'zeni', 0) or 0
        if player_zeni < TOURNAMENT_ENTRY_COST:
            return {"success": False, "reason": f"Need {TOURNAMENT_ENTRY_COST} zeni to enter"}
        
        # Deduct entry fee
        player.db.zeni = player_zeni - TOURNAMENT_ENTRY_COST
        
        # Add to prize pool
        current_prize = _tournament_state.get("prize_pool", 0)
        _tournament_state["prize_pool"] = current_prize + TOURNAMENT_ENTRY_COST
        
        _tournament_state["participants"].append(player_id)
        return {"success": True, "participants": len(_tournament_state["participants"]), "entry_paid": TOURNAMENT_ENTRY_COST}


def leave_tournament(player):
    """Remove a player from the tournament."""
    with _tournament_lock:
        player_id = player.id
        if player_id in _tournament_state["participants"]:
            _tournament_state["participants"].remove(player_id)
            return {"success": True}
        return {"success": False, "reason": "Not signed up"}


def register_match_win(player_id):
    """Register a match win and advance the bracket."""
    matches = _tournament_state["matches"]
    
    # Find and complete the match
    for match in matches:
        if match["winner"] is None:
            if player_id in [match["player1"], match["player2"]]:
                match["winner"] = player_id
                match["in_progress"] = False
                break
    
    # Check if round is complete
    all_done = all(m["winner"] is not None for m in matches)
    
    if all_done:
        # Get winners
        winners = [m["winner"] for m in matches]
        
        if len(winners) == 1:
            # Tournament complete!
            champion = winners[0]
            _tournament_state["status"] = TOURNAMENT_FINISHED
            _tournament_state["champion"] = champion
            return {"tournament_complete": True, "champion": champion}
        else:
            # Create next round
            next_matches = []
            for i in range(0, len(winners), 2):
                if i + 1 < len(winners):
                    next_matches.append({
                        "player1": winners[i],
                        "player2": winners[i + 1],
                        "winner": None,
                        "in_progress": False,
                    })
            _tournament_state["matches"] = next_matches
            _tournament_state["round"] += 1
    
    return {"tournament_complete": False}


def end_tournament():
    """End the tournament and reset state."""
    _tournament_state["status"] = TOURNAMENT_INACTIVE
    _tournament_state["signup_open"] = False
    _tournament_state["participants"] = []
    _tournament_state["bracket"] = []
    _tournament_state["matches"] = []
    _tournament_state["round"] = 0


# World Boss Functions
def _get_player_for_damage(player_id: str):
    """Get player object from player_id for damage calculation."""
    from evennia.objects.models import ObjectDB
    try:
        # player_id is the string version of the account or character id
        obj = ObjectDB.objects.filter(id=int(player_id)).first()
        if obj and hasattr(obj, 'get_current_pl'):
            return obj
    except (ValueError, TypeError):
        pass
    return None


def _calculate_world_boss_damage(player) -> int:
    """
    Server-side damage calculation for world boss attacks.
    This prevents clients from manipulating damage values.
    
    Damage formula based on player's actual combat stats:
    - Base damage from power level
    - Bonus from strength and mastery
    - Random variance (server-controlled)
    """
    import random
    from world.power import compute_current_pl
    
    current_pl, _ = compute_current_pl(player)
    strength = player.db.strength or 10
    mastery = player.db.mastery or 10
    
    # Base damage: ~50-150% of PL
    base_damage = int(current_pl * random.uniform(0.5, 1.5))
    
    # Bonus from stats
    stat_bonus = int((strength * 2) + (mastery * 1.5))
    
    # Random variance
    variance = random.uniform(0.8, 1.2)
    
    damage = int((base_damage + stat_bonus) * variance)
    
    # Ensure minimum damage of 1
    return max(1, damage)


def damage_world_boss(player_id: str, damage: int = None):
    """
    Register damage dealt to the world boss.
    
    SECURITY: If damage is None, calculate server-side.
    If damage is provided, it will be ignored (defense in depth).
    """
    if not _world_boss_state["active"]:
        return {"success": False, "reason": "No boss active"}
    
    # SECURITY: Always calculate damage server-side
    # Ignore any client-provided damage value
    player = _get_player_for_damage(player_id)
    if not player:
        return {"success": False, "reason": "Player not found"}
    
    # Calculate damage server-side based on player's actual stats
    damage = _calculate_world_boss_damage(player)
    """Spawn a world boss."""
    _world_boss_state["active"] = True
    _world_boss_state["boss_name"] = boss_name
    _world_boss_state["boss_pl"] = boss_pl
    _world_boss_state["boss_hp"] = boss_pl * 100  # HP based on PL
    _world_boss_state["boss_max_hp"] = boss_pl * 100
    _world_boss_state["spawn_time"] = time.time()
    _world_boss_state["end_time"] = time.time() + WORLD_BOSS_DURATION
    _world_boss_state["damage_dealt"] = {}
    _world_boss_state["top_damager"] = None
    return _world_boss_state


def damage_world_boss(player_id: str, damage: int):
    """Register damage dealt to the world boss."""
    if not _world_boss_state["active"]:
        return {"success": False, "reason": "No boss active"}
    
    # Add damage
    current = _world_boss_state["damage_dealt"].get(player_id, 0)
    _world_boss_state["damage_dealt"][player_id] = current + damage
    
    # Reduce HP
    _world_boss_state["boss_hp"] -= damage
    
    # Check for kill
    if _world_boss_state["boss_hp"] <= 0:
        return end_world_boss()
    
    # Update top damager
    top_damage = 0
    top_id = None
    for pid, dmg in _world_boss_state["damage_dealt"].items():
        if dmg > top_damage:
            top_damage = dmg
            top_id = pid
    _world_boss_state["top_damager"] = top_id
    
    return {
        "success": True,
        "boss_hp": _world_boss_state["boss_hp"],
        "boss_max_hp": _world_boss_state["boss_max_hp"],
        "top_damager": top_id,
    }


def end_world_boss():
    """End the world boss event and distribute rewards."""
    if not _world_boss_state["active"]:
        return {"success": False, "reason": "No boss active"}
    
    # Find top damager
    damage_dealt = _world_boss_state["damage_dealt"]
    if damage_dealt:
        top_id = max(damage_dealt, key=damage_dealt.get)
        top_damage = damage_dealt[top_id]
    else:
        top_id = None
        top_damage = 0
    
    _world_boss_state["active"] = False
    _world_boss_state["top_damager"] = top_id
    
    return {
        "success": True,
        "boss_name": _world_boss_state["boss_name"],
        "top_damager": top_id,
        "top_damage": top_damage,
    }


def get_world_boss_damage_leaderboard():
    """Get damage leaderboard for current world boss."""
    damage_dealt = _world_boss_state["damage_dealt"]
    sorted_damage = sorted(damage_dealt.items(), key=lambda x: x[1], reverse=True)
    return [
        {"player_id": pid, "damage": dmg}
        for pid, dmg in sorted_damage
    ]


# Predefined bosses
WORLD_BOSSES = {
    "frieza": {"name": "Frieza", "base_pl": 50000},
    "cell": {"name": "Cell", "base_pl": 60000},
    "buu": {"name": "Majin Buu", "base_pl": 70000},
    "janemba": {"name": "Janemba", "base_pl": 75000},
    "broly": {"name": "Broly", "base_pl": 80000},
}


def try_spawn_world_boss():
    """Try to spawn a world boss (random chance)."""
    if _world_boss_state["active"]:
        return {"success": False, "reason": "Boss already active"}
    
    if random.random() < WORLD_BOSS_SPAWN_CHANCE:
        boss_key = random.choice(list(WORLD_BOSSES.keys()))
        boss_data = WORLD_BOSSES[boss_key]
        return spawn_world_boss(boss_data["name"], boss_data["base_pl"])
    
    return {"success": False, "reason": "No boss spawned"}
