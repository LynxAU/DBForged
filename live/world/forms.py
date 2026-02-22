"""
Data-driven transformation catalog.
"""

FORMS = {
    # Super Saiyan forms
    "super_saiyan": {
        "name": "Super Saiyan",
        "race": "saiyan",
        "pl_multiplier": 1.8,
        "speed_bias": 1.08,
        "mastery_bias": 1.04,
        "drain_per_tick": 6,
        "drain_per_tech": 4,
        "mastery_drain_reduction": 0.012,
        "vfx_id": "vfx_aura_ssj",
    },
    "super_saiyan_2": {
        "name": "Super Saiyan 2",
        "race": "saiyan",
        "pl_multiplier": 2.4,
        "speed_bias": 1.18,
        "mastery_bias": 1.08,
        "drain_per_tick": 9,
        "drain_per_tech": 6,
        "mastery_drain_reduction": 0.015,
        "vfx_id": "vfx_aura_ssj2",
    },
    "super_saiyan_3": {
        "name": "Super Saiyan 3",
        "race": "saiyan",
        "pl_multiplier": 3.2,
        "speed_bias": 1.25,
        "mastery_bias": 1.12,
        "drain_per_tick": 15,
        "drain_per_tech": 10,
        "mastery_drain_reduction": 0.018,
        "vfx_id": "vfx_aura_ssj3",
    },
    "super_saiyan_god": {
        "name": "Super Saiyan God",
        "race": "saiyan",
        "pl_multiplier": 4.0,
        "speed_bias": 1.30,
        "mastery_bias": 1.15,
        "drain_per_tick": 12,
        "drain_per_tech": 8,
        "mastery_drain_reduction": 0.020,
        "vfx_id": "vfx_aura_ssjg",
    },
    "super_saiyan_blue": {
        "name": "Super Saiyan Blue",
        "race": "saiyan",
        "pl_multiplier": 5.0,
        "speed_bias": 1.35,
        "mastery_bias": 1.20,
        "drain_per_tick": 18,
        "drain_per_tech": 12,
        "mastery_drain_reduction": 0.022,
        "vfx_id": "vfx_aura_ssgb",
    },
    
    # Human potential
    "potential_unleashed": {
        "name": "Potential Unleashed",
        "race": "human",
        "pl_multiplier": 2.2,
        "speed_bias": 1.10,
        "mastery_bias": 1.12,
        "drain_per_tick": 5,
        "drain_per_tech": 3,
        "mastery_drain_reduction": 0.015,
        "vfx_id": "vfx_aura_potential",
    },
    
    # Frost Demon forms
    "frost_aura": {
        "name": "Frost Aura",
        "race": "frost_demon",
        "pl_multiplier": 1.6,
        "speed_bias": 1.06,
        "mastery_bias": 1.06,
        "drain_per_tick": 5,
        "drain_per_tech": 3,
        "mastery_drain_reduction": 0.010,
        "vfx_id": "vfx_aura_frost",
    },
    "true_form": {
        "name": "True Form",
        "race": "frost_demon",
        "pl_multiplier": 2.8,
        "speed_bias": 1.15,
        "mastery_bias": 1.10,
        "drain_per_tick": 12,
        "drain_per_tech": 8,
        "mastery_drain_reduction": 0.012,
        "vfx_id": "vfx_aura_true",
    },
    
    # Android forms
    "android_ultimate": {
        "name": "Ultimate Android",
        "race": "android",
        "pl_multiplier": 2.0,
        "speed_bias": 1.05,
        "mastery_bias": 1.08,
        "drain_per_tick": 0,  # Androids don't drain ki!
        "drain_per_tech": 0,
        "mastery_drain_reduction": 0.0,
        "vfx_id": "vfx_aura_android",
    },
    
    # Namekian fusion-like
    "namekian_fusion": {
        "name": "Namekian Warrior",
        "race": "namekian",
        "pl_multiplier": 1.9,
        "speed_bias": 1.04,
        "mastery_bias": 1.06,
        "drain_per_tick": 7,
        "drain_per_tech": 5,
        "mastery_drain_reduction": 0.012,
        "vfx_id": "vfx_aura_namek",
    },
}


def get_form(key_or_name):
    needle = (key_or_name or "").strip().lower()
    if needle in FORMS:
        return needle, FORMS[needle]
    for key, data in FORMS.items():
        if data["name"].lower() == needle:
            return key, data
    return None, None
