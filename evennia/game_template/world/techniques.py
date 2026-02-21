"""
Data-driven technique catalog.
"""

TECHNIQUES = {
    "ki_blast": {
        "name": "Ki Blast",
        "category": "blast",
        "ki_cost": 10,
        "cooldown": 2.5,
        "cast_time": 0.0,
        "tags": ["ranged", "damage"],
        "vfx_id": "vfx_ki_blast",
        "scaling": {"base": 14, "strength": 0.45, "mastery": 0.25, "pl": 0.0017},
    },
    "kame_wave": {
        "name": "Kame Wave",
        "category": "beam",
        "ki_cost": 24,
        "cooldown": 6.0,
        "cast_time": 0.5,
        "tags": ["beam", "damage"],
        "vfx_id": "vfx_kame_wave",
        "scaling": {"base": 24, "strength": 0.55, "mastery": 0.35, "pl": 0.0024},
    },
    "solar_flare": {
        "name": "Solar Flare",
        "category": "control",
        "ki_cost": 16,
        "cooldown": 9.0,
        "cast_time": 0.0,
        "tags": ["stun", "interrupt"],
        "vfx_id": "vfx_solar_flare",
        "effect": {"type": "stun", "duration": 2.0},
    },
    "guard": {
        "name": "Guard",
        "category": "defense",
        "ki_cost": 8,
        "cooldown": 5.0,
        "cast_time": 0.0,
        "tags": ["defense", "self"],
        "vfx_id": "vfx_guard_sphere",
        "effect": {"type": "guard", "duration": 3.0, "reduction": 0.45},
    },
    "afterimage_dash": {
        "name": "Afterimage Dash",
        "category": "movement",
        "ki_cost": 14,
        "cooldown": 7.5,
        "cast_time": 0.0,
        "tags": ["movement", "evasion"],
        "vfx_id": "vfx_afterimage",
        "effect": {"type": "afterimage", "duration": 2.0},
    },
    "vanish_strike": {
        "name": "Vanish Strike",
        "category": "interrupt",
        "ki_cost": 18,
        "cooldown": 8.5,
        "cast_time": 0.0,
        "tags": ["melee", "interrupt", "damage"],
        "vfx_id": "vfx_vanish_strike",
        "scaling": {"base": 18, "strength": 0.6, "mastery": 0.3, "pl": 0.0018},
    },
}

STARTER_TECHNIQUES = [
    "ki_blast",
    "kame_wave",
    "solar_flare",
    "guard",
    "afterimage_dash",
    "vanish_strike",
]


def get_technique(key_or_name):
    needle = (key_or_name or "").strip().lower()
    if needle in TECHNIQUES:
        return needle, TECHNIQUES[needle]
    for key, data in TECHNIQUES.items():
        if data["name"].lower() == needle:
            return key, data
    return None, None


def is_beam(tech_key):
    return "beam" in TECHNIQUES.get(tech_key, {}).get("tags", [])
