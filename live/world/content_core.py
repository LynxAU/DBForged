"""
Shared content helpers for techniques, racials and transformations.
"""

from __future__ import annotations

from copy import deepcopy


def deep_merge(base, updates):
    """
    Merge nested dicts for content definitions without mutating inputs.
    """
    result = deepcopy(base)
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def build_registry(items):
    """
    Convert iterable[(key, data)] to a validated dict with stable key injection.
    """
    registry = {}
    for key, data in items:
        if key in registry:
            raise ValueError(f"Duplicate content key: {key}")
        entry = dict(data)
        entry.setdefault("id", key)
        registry[key] = entry
    return registry


def find_by_key_or_name(registry, key_or_name):
    needle = (key_or_name or "").strip().lower()
    if needle in registry:
        return needle, registry[needle]
    for key, data in registry.items():
        if data.get("name", "").lower() == needle:
            return key, data
        for alias in data.get("aliases", []):
            if str(alias).lower() == needle:
                return key, data
    return None, None


def summarize_effect(entry):
    """
    Short UI summary used by web and in-game listings.
    """
    effect = entry.get("effect", {})
    scaling = entry.get("scaling", {})
    tags = entry.get("tags", [])
    if effect.get("type") == "damage":
        base = effect.get("base_damage", scaling.get("base", 0))
        kind = effect.get("damage_kind", "damage")
        return f"{kind.title()} {base}+ scaling"
    if effect.get("type") == "stun":
        return f"Stun {effect.get('duration', 0)}s"
    if effect.get("type") == "blind":
        return f"Flash/Blind {effect.get('duration', 0)}s"
    if effect.get("type") == "guard":
        return f"Guard {int(effect.get('reduction', 0)*100)}% {effect.get('duration', 0)}s"
    if effect.get("type") == "movement":
        return effect.get("summary", "Mobility technique")
    if effect.get("type") == "transform":
        return effect.get("summary", "Transformation")
    if effect.get("type") == "passive":
        return effect.get("summary", "Passive trait")
    if effect.get("type") == "resource":
        return effect.get("summary", "Resource control")
    if "beam" in tags:
        return "Beam attack with struggle hook"
    if "utility" in tags:
        return "Utility technique"
    return effect.get("summary", "Technique")


def make_stub_result(kind, content_key, caller=None, target=None, payload=None):
    return {
        "kind": kind,
        "content_key": content_key,
        "caller": caller,
        "target": target,
        "payload": payload or {},
        "stub": True,
        "ready_for_combat_resolution": True,
    }
