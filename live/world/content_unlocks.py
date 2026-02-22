"""
Central unlock source registry covering all techniques, transformations and racials.
"""

from __future__ import annotations

from collections import defaultdict

from world.forms import FORMS
from world.npc_content import NPC_DEFINITIONS
from world.quests import QUESTLINES
from world.racials import RACIALS
from world.techniques import TECHNIQUES


DEFAULT_PLACEHOLDER_TRAINER = "combat_instructor_network"
DEFAULT_PLACEHOLDER_QUEST = "open_world_discovery"


def _base_entry(kind, key, name):
    return {
        "kind": kind,
        "id": key,
        "name": name,
        "unlock_source": {
            "type": "placeholder",
            "trainer": DEFAULT_PLACEHOLDER_TRAINER,
            "quest": DEFAULT_PLACEHOLDER_QUEST,
            "race": None,
            "notes": "Placeholder mapping; tune later in content pass.",
        },
    }


def _seed_registry():
    registry = {}
    for key, data in TECHNIQUES.items():
        registry[("technique", key)] = _base_entry("technique", key, data["name"])
        prereq = data.get("prerequisites", {})
        if prereq.get("race"):
            registry[("technique", key)]["unlock_source"]["race"] = prereq["race"]
        if prereq.get("race_any"):
            registry[("technique", key)]["unlock_source"]["race"] = list(prereq["race_any"])
        if prereq.get("trainer"):
            registry[("technique", key)]["unlock_source"]["trainer"] = prereq["trainer"]
            registry[("technique", key)]["unlock_source"]["type"] = "trainer"
        if prereq.get("quest"):
            registry[("technique", key)]["unlock_source"]["quest"] = prereq["quest"]
            registry[("technique", key)]["unlock_source"]["type"] = "quest"
    for key, data in FORMS.items():
        registry[("transformation", key)] = _base_entry("transformation", key, data["name"])
        prereq = data.get("prerequisites", {})
        if prereq.get("race"):
            registry[("transformation", key)]["unlock_source"]["race"] = prereq["race"]
            registry[("transformation", key)]["unlock_source"]["type"] = "race"
        if prereq.get("race_any"):
            registry[("transformation", key)]["unlock_source"]["race"] = list(prereq["race_any"])
            registry[("transformation", key)]["unlock_source"]["type"] = "race+quest"
        if prereq.get("trainer"):
            registry[("transformation", key)]["unlock_source"]["trainer"] = prereq["trainer"]
            registry[("transformation", key)]["unlock_source"]["type"] = "trainer"
        if prereq.get("quest"):
            registry[("transformation", key)]["unlock_source"]["quest"] = prereq["quest"]
            registry[("transformation", key)]["unlock_source"]["type"] = "quest"
        if data.get("special_system") == "lssj":
            registry[("transformation", key)]["unlock_source"]["type"] = "special_system"
            registry[("transformation", key)]["unlock_source"]["trainer"] = "broly"
            registry[("transformation", key)]["unlock_source"]["quest"] = "legendary_control_protocol"
            registry[("transformation", key)]["unlock_source"]["notes"] = "Delegates to LSSJ progression system."
    for key, data in RACIALS.items():
        registry[("racial", key)] = _base_entry("racial", key, data["name"])
        registry[("racial", key)]["unlock_source"] = {
            "type": "race_innate",
            "trainer": None,
            "quest": None,
            "race": data["race"],
            "notes": "Innate racial trait choice available to this race.",
        }
    return registry


def _apply_trainer_rewards(registry):
    for npc_key, npc in NPC_DEFINITIONS.items():
        rewards = npc.get("trainer_rewards", {})
        for tech_key in rewards.get("techniques", []):
            if ("technique", tech_key) in registry:
                registry[("technique", tech_key)]["unlock_source"].update(
                    {"type": "trainer", "trainer": npc_key}
                )
        for form_key in rewards.get("forms", []):
            if ("transformation", form_key) in registry:
                registry[("transformation", form_key)]["unlock_source"].update(
                    {"type": "trainer", "trainer": npc_key}
                )


def _apply_quest_rewards(registry):
    for quest_key, quest in QUESTLINES.items():
        rewards = quest.get("rewards", {})
        for tech_key in rewards.get("techniques", []):
            if ("technique", tech_key) in registry:
                registry[("technique", tech_key)]["unlock_source"].update(
                    {"type": "quest", "quest": quest_key, "trainer": quest.get("giver")}
                )
        for form_key in rewards.get("forms", []):
            if ("transformation", form_key) in registry:
                registry[("transformation", form_key)]["unlock_source"].update(
                    {"type": "quest", "quest": quest_key, "trainer": quest.get("giver")}
                )


def build_unlock_registry():
    registry = _seed_registry()
    _apply_trainer_rewards(registry)
    _apply_quest_rewards(registry)
    return registry


UNLOCK_REGISTRY = build_unlock_registry()


def get_unlock_source(kind, key):
    entry = UNLOCK_REGISTRY.get((kind, key))
    return dict(entry.get("unlock_source")) if entry else None


def get_unlock_label(kind, key):
    source = get_unlock_source(kind, key) or {}
    parts = []
    if source.get("race"):
        race = source["race"]
        if isinstance(race, list):
            parts.append("Race: " + "/".join(str(r).replace("_", " ").title() for r in race))
        else:
            parts.append("Race: " + str(race).replace("_", " ").title())
    if source.get("trainer"):
        trainer_name = NPC_DEFINITIONS.get(source["trainer"], {}).get("name", source["trainer"])
        parts.append(f"Trainer: {trainer_name}")
    if source.get("quest"):
        quest_title = QUESTLINES.get(source["quest"], {}).get("title", source["quest"])
        parts.append(f"Quest: {quest_title}")
    if not parts:
        parts.append(source.get("notes") or "Unknown")
    return " | ".join(parts)


def get_trainer_reward_map():
    out = defaultdict(lambda: {"techniques": [], "transformations": [], "questlines": []})
    for (kind, key), entry in UNLOCK_REGISTRY.items():
        source = entry["unlock_source"]
        trainer = source.get("trainer")
        if not trainer:
            continue
        bucket = out[trainer]
        if kind == "technique":
            bucket["techniques"].append(key)
        elif kind == "transformation":
            bucket["transformations"].append(key)
    for quest in QUESTLINES.values():
        out[quest["giver"]]["questlines"].append(quest["id"])
    return {k: {kk: sorted(set(vv)) for kk, vv in v.items()} for k, v in out.items()}


def validate_unlock_coverage():
    errors = []
    for key in TECHNIQUES:
        if ("technique", key) not in UNLOCK_REGISTRY:
            errors.append(f"Missing technique unlock mapping: {key}")
    for key in FORMS:
        if ("transformation", key) not in UNLOCK_REGISTRY:
            errors.append(f"Missing transformation unlock mapping: {key}")
    for key in RACIALS:
        if ("racial", key) not in UNLOCK_REGISTRY:
            errors.append(f"Missing racial unlock mapping: {key}")
    return errors
