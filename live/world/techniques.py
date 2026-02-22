"""
Data-driven technique catalog.
"""

TECHNIQUES = {
    # Basic attacks
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
    
    # Beam attacks (core to DB combat)
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
    "galick_gun": {
        "name": "Galick Gun",
        "category": "beam",
        "ki_cost": 22,
        "cooldown": 5.5,
        "cast_time": 0.4,
        "tags": ["beam", "damage"],
        "vfx_id": "vfx_galick_gun",
        "scaling": {"base": 26, "strength": 0.58, "mastery": 0.36, "pl": 0.0025},
    },
    "final_flash": {
        "name": "Final Flash",
        "category": "beam",
        "ki_cost": 45,
        "cooldown": 12.0,
        "cast_time": 1.0,
        "tags": ["beam", "damage", "heavy"],
        "vfx_id": "vfx_final_flash",
        "scaling": {"base": 45, "strength": 0.75, "mastery": 0.50, "pl": 0.0035},
    },
    "masenko": {
        "name": "Masenko",
        "category": "beam",
        "ki_cost": 28,
        "cooldown": 7.0,
        "cast_time": 0.6,
        "tags": ["beam", "damage", "fast"],
        "vfx_id": "vfx_masenko",
        "scaling": {"base": 28, "strength": 0.60, "mastery": 0.38, "pl": 0.0026},
    },
    "special_beam_cannon": {
        "name": "Special Beam Cannon",
        "category": "beam",
        "ki_cost": 35,
        "cooldown": 10.0,
        "cast_time": 1.2,
        "tags": ["beam", "pierce", "heavy"],
        "vfx_id": "vfx_special_beam_cannon",
        "scaling": {"base": 40, "strength": 0.70, "mastery": 0.45, "pl": 0.0030},
        "effect": {"type": "pierce", "reduction": 0.3},
    },
    "death_beam": {
        "name": "Death Beam",
        "category": "beam",
        "ki_cost": 20,
        "cooldown": 4.0,
        "cast_time": 0.2,
        "tags": ["beam", "damage", "fast"],
        "vfx_id": "vfx_death_beam",
        "scaling": {"base": 22, "strength": 0.52, "mastery": 0.32, "pl": 0.0022},
    },
    "big_bang_attack": {
        "name": "Big Bang Attack",
        "category": "aoe",
        "ki_cost": 50,
        "cooldown": 14.0,
        "cast_time": 0.8,
        "tags": ["aoe", "damage", "heavy"],
        "vfx_id": "vfx_big_bang",
        "scaling": {"base": 48, "strength": 0.78, "mastery": 0.52, "pl": 0.0038},
    },
    "burning_attack": {
        "name": "Burning Attack",
        "category": "beam",
        "ki_cost": 30,
        "cooldown": 8.0,
        "cast_time": 0.5,
        "tags": ["beam", "damage"],
        "vfx_id": "vfx_burning_attack",
        "scaling": {"base": 30, "strength": 0.62, "mastery": 0.40, "pl": 0.0027},
    },
    "finish_buster": {
        "name": "Finish Buster",
        "category": "beam",
        "ki_cost": 38,
        "cooldown": 9.0,
        "cast_time": 0.7,
        "tags": ["beam", "damage", "heavy"],
        "vfx_id": "vfx_finish_buster",
        "scaling": {"base": 38, "strength": 0.68, "mastery": 0.44, "pl": 0.0029},
    },
    
    # Melee attacks
    "dragon_fist": {
        "name": "Dragon Fist",
        "category": "melee",
        "ki_cost": 35,
        "cooldown": 10.0,
        "cast_time": 0.3,
        "tags": ["melee", "damage", "heavy"],
        "vfx_id": "vfx_dragon_fist",
        "scaling": {"base": 42, "strength": 0.80, "mastery": 0.48, "pl": 0.0032},
    },
    "wolf_fang_fist": {
        "name": "Wolf Fang Fist",
        "category": "melee",
        "ki_cost": 18,
        "cooldown": 5.0,
        "cast_time": 0.0,
        "tags": ["melee", "damage", "combo"],
        "vfx_id": "vfx_wolf_fang",
        "scaling": {"base": 20, "strength": 0.65, "mastery": 0.38, "pl": 0.0020},
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
    
    # Control/Utility
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
    "mafuba": {
        "name": "Mafuba",
        "category": "control",
        "ki_cost": 60,
        "cooldown": 30.0,
        "cast_time": 1.5,
        "tags": ["seal", "control"],
        "vfx_id": "vfx_mafuba",
        "effect": {"type": "seal", "duration": 8.0},
    },
    "hellzone_grenade": {
        "name": "Hellzone Grenade",
        "category": "trap",
        "ki_cost": 40,
        "cooldown": 15.0,
        "cast_time": 0.5,
        "tags": ["trap", "aoe", "damage"],
        "vfx_id": "vfx_hellzone",
        "scaling": {"base": 35, "strength": 0.65, "mastery": 0.42, "pl": 0.0028},
    },
    
    # Defense
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
    "android_barrier": {
        "name": "Android Barrier",
        "category": "defense",
        "ki_cost": 15,
        "cooldown": 8.0,
        "cast_time": 0.0,
        "tags": ["defense", "self", "barrier"],
        "vfx_id": "vfx_android_barrier",
        "effect": {"type": "guard", "duration": 4.0, "reduction": 0.65},
    },
    
    # Movement/Evasion
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
    
    # Support
    "ki_charge": {
        "name": "Ki Charge",
        "category": "support",
        "ki_cost": 0,
        "cooldown": 0.0,
        "cast_time": 0.0,
        "tags": ["support", "self", "resource"],
        "vfx_id": "vfx_charge_glow",
        "effect": {"type": "charge", "duration": 6.0},
    },
}

STARTER_TECHNIQUES = [
    "ki_blast",
    "kame_wave",
    "solar_flare",
    "guard",
    "afterimage_dash",
    "vanish_strike",
    "galick_gun",
    "burning_attack",
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
