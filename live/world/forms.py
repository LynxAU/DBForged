"""
Data-driven transformation catalog.
"""

FORMS = {
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
    "potential_unleashed": {
        "name": "Potential Unleashed",
        "race": "human",
        "stub": True,
    },
    "frost_aura": {
        "name": "Frost Aura",
        "race": "frost_demon",
        "stub": True,
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
