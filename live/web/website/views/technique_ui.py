"""
Technique UI page for browsing DBForged techniques/racials/forms.
"""

from __future__ import annotations

import json

from django.shortcuts import render

from world.content_unlocks import get_unlock_label
from world.forms import FORMS
from world.racials import RACIALS
from world.techniques import TECHNIQUES


def _safe_active_character(request):
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return None
    try:
        chars = list(getattr(user, "characters", []) or [])
    except Exception:
        chars = []
    for char in chars:
        if getattr(char, "is_typeclass", None):
            return char
    return chars[0] if chars else None


def _serialize_techniques():
    items = []
    for key, data in sorted(TECHNIQUES.items(), key=lambda item: (item[1].get("category", ""), item[1]["name"])):
        items.append(
            {
                "kind": "technique",
                "id": key,
                "name": data["name"],
                "category": data.get("category", "misc"),
                "tags": data.get("tags", []),
                "cost": data.get("resource_costs", {}).get("ki", 0),
                "cooldown": data.get("cooldown", 0),
                "summary": data.get("ui_summary", ""),
                "description": data.get("description", ""),
                "unlock_source": get_unlock_label("technique", key),
                "prerequisites": data.get("prerequisites", {}),
            }
        )
    return items


def _serialize_racials():
    items = []
    for key, data in sorted(RACIALS.items(), key=lambda item: (item[1].get("race", ""), item[1]["name"])):
        items.append(
            {
                "kind": "racial",
                "id": key,
                "name": data["name"],
                "category": "passive/racial",
                "tags": data.get("tags", []),
                "cost": data.get("resource_costs", {}).get("ki", 0),
                "cooldown": data.get("cooldown", 0),
                "summary": data.get("ui_summary", ""),
                "description": data.get("description", ""),
                "unlock_source": get_unlock_label("racial", key),
                "race": data.get("race"),
            }
        )
    return items


def _serialize_forms():
    items = []
    for key, data in sorted(FORMS.items(), key=lambda item: (item[1].get("tier", 0), item[1]["name"])):
        mods = data.get("modifiers", {})
        items.append(
            {
                "kind": "transformation",
                "id": key,
                "name": data["name"],
                "category": "transformation",
                "tags": ["transformation", data.get("race", "unknown")],
                "cost": data.get("resource_drain", {}).get("ki_per_tick", 0),
                "cooldown": 0,
                "summary": (
                    f"Tier {data.get('tier')} | PL x{mods.get('pl_factor',1.0):.2f} | "
                    f"Drain {data.get('resource_drain',{}).get('ki_per_tick',0)}/tick"
                ),
                "description": data.get("description", ""),
                "unlock_source": get_unlock_label("transformation", key),
                "race": data.get("race"),
            }
        )
    return items


def technique_ui(request):
    char = _safe_active_character(request)
    loadout = []
    if char:
        for tech_key in list(char.db.equipped_techniques or [])[:4]:
            if tech_key in TECHNIQUES:
                t = TECHNIQUES[tech_key]
                loadout.append(
                    {
                        "id": tech_key,
                        "name": t["name"],
                        "cost": t.get("ki_cost", 0),
                        "cooldown": t.get("cooldown", 0),
                        "summary": t.get("ui_summary", ""),
                    }
                )

    payload = {
        "techniques": _serialize_techniques(),
        "racials": _serialize_racials(),
        "transformations": _serialize_forms(),
        "loadout": loadout,
        "counts": {
            "techniques": len(TECHNIQUES),
            "racials": len(RACIALS),
            "transformations": len(FORMS),
        },
    }
    return render(
        request,
        "website/db_techniques.html",
        {
            "page_title": "DBForged Technique UI",
            "catalog_json": json.dumps(payload),
        },
    )
