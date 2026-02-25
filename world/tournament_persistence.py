"""
Tournament and World Boss persistence script.

This module provides persistent storage for tournament and world boss state
using Evennia's GlobalScript system. This ensures state survives server restarts.
"""

from __future__ import annotations

import copy
import time

from evennia.scripts.scripts import DefaultScript

# Default tournament state
_DEFAULT_TOURNAMENT_STATE = {
    "status": "inactive",
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

# Default world boss state
_DEFAULT_WORLD_BOSS_STATE = {
    "active": False,
    "boss_name": "",
    "boss_pl": 0,
    "boss_hp": 0,
    "boss_max_hp": 0,
    "spawn_time": 0,
    "end_time": 0,
    "damage_dealt": {},
    "reward_zeni": 5000,
    "top_damager": None,
}


class TournamentStateScript(DefaultScript):
    """
    Persistent script that stores tournament and world boss state.
    
    This ensures tournament progress and active world boss events
    survive server restarts.
    """

    key = "tournament_state"
    desc = "Persists tournament and world boss state"
    persistent = True
    interval = 0  # No automatic tick - we manage state directly

    def at_script_creation(self):
        """Initialize default state on first creation."""
        self.db.tournament_state = copy.deepcopy(_DEFAULT_TOURNAMENT_STATE)
        self.db.world_boss_state = copy.deepcopy(_DEFAULT_WORLD_BOSS_STATE)

    # Tournament state methods
    def get_tournament_state(self) -> dict:
        """Get current tournament state."""
        return self.db.tournament_state

    def set_tournament_state(self, state: dict):
        """Set tournament state."""
        self.db.tournament_state = state

    def update_tournament(self, **kwargs):
        """Update specific tournament state fields."""
        state = self.db.tournament_state
        for key, value in kwargs.items():
            if key in state:
                state[key] = value
        self.db.tournament_state = state

    # World boss state methods
    def get_world_boss_state(self) -> dict:
        """Get current world boss state."""
        return self.db.world_boss_state

    def set_world_boss_state(self, state: dict):
        """Set world boss state."""
        self.db.world_boss_state = state

    def update_world_boss(self, **kwargs):
        """Update specific world boss state fields."""
        state = self.db.world_boss_state
        for key, value in kwargs.items():
            if key in state:
                state[key] = value
        self.db.world_boss_state = state

    def reset_tournament(self):
        """Reset tournament to default state."""
        self.db.tournament_state = copy.deepcopy(_DEFAULT_TOURNAMENT_STATE)

    def reset_world_boss(self):
        """Reset world boss to default state."""
        self.db.world_boss_state = copy.deepcopy(_DEFAULT_WORLD_BOSS_STATE)


# Helper functions to get the persistent state
def get_persistent_tournament_state() -> dict:
    """Get the tournament state script or return defaults."""
    script = TournamentStateScript.objects.first()
    if script:
        return script.get_tournament_state()
    return copy.deepcopy(_DEFAULT_TOURNAMENT_STATE)


def get_persistent_world_boss_state() -> dict:
    """Get the world boss state script or return defaults."""
    script = TournamentStateScript.objects.first()
    if script:
        return script.get_world_boss_state()
    return copy.deepcopy(_DEFAULT_WORLD_BOSS_STATE)


def ensure_tournament_script():
    """Ensure the tournament state script exists."""
    script = TournamentStateScript.objects.first()
    if not script:
        script = TournamentStateScript()
        script.save()
    return script
