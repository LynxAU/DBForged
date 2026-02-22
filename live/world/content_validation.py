"""
Validation and count helpers for DBForged content-completeness checks.
"""

from __future__ import annotations

from world.content_unlocks import validate_unlock_coverage
from world.forms import FORMS, validate_form_registry
from world.npc_content import NPC_DEFINITIONS
from world.quests import QUESTLINES
from world.racials import PLAYABLE_RACES, RACIALS, get_racials_for_race, validate_racial_registry
from world.techniques import TECHNIQUES, validate_technique_registry


def get_content_counts():
    per_race = {race: len(get_racials_for_race(race)) for race in PLAYABLE_RACES}
    return {
        "techniques": len(TECHNIQUES),
        "transformations": len(FORMS),
        "racials_total": len(RACIALS),
        "races": len(PLAYABLE_RACES),
        "racials_per_race": per_race,
        "npcs": len(NPC_DEFINITIONS),
        "questlines": len(QUESTLINES),
    }


def validate_all_content():
    return {
        "counts": get_content_counts(),
        "errors": {
            "techniques": validate_technique_registry(),
            "transformations": validate_form_registry(),
            "racials": validate_racial_registry(),
            "unlocks": validate_unlock_coverage(),
        },
    }


def has_validation_errors(result=None):
    result = result or validate_all_content()
    return any(bool(items) for items in result.get("errors", {}).values())
