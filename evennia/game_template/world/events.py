"""
Structured JSON event emission for future sprite clients.
"""

from __future__ import annotations

import json
import time

EVENT_PREFIX = "@event "


def _safe_stats(entity):
    hp_max = max(1, entity.db.hp_max or 1)
    ki_max = max(1, entity.db.ki_max or 1)
    current_pl, breakdown = entity.get_current_pl()
    return {
        "hp": max(0, entity.db.hp_current or 0),
        "hp_max": hp_max,
        "ki": max(0, entity.db.ki_current or 0),
        "ki_max": ki_max,
        "pl": current_pl,
        "displayed_pl": breakdown.get("displayed_pl", current_pl),
    }


def emit_event(receiver, event_type, payload):
    packet = {"type": event_type, "ts": round(time.time(), 3), **payload}
    receiver.msg(EVENT_PREFIX + json.dumps(packet, separators=(",", ":")))


def emit_event_room(room, event_type, payload, exclude=None):
    packet = {"type": event_type, "ts": round(time.time(), 3), **payload}
    room.msg_contents(EVENT_PREFIX + json.dumps(packet, separators=(",", ":")), exclude=exclude or [])


def emit_entity_delta(entity, recipients=None):
    stats = _safe_stats(entity)
    payload = {
        "entity": {
            "id": entity.id,
            "name": entity.key,
            "room": entity.location.id if entity.location else None,
            "room_name": entity.location.key if entity.location else None,
            "position": {"x": 0, "y": 0, "layer": 0},
            "sprite_id": entity.db.sprite_id or "sprite_humanoid_default",
            **stats,
        }
    }
    if recipients:
        for obj in recipients:
            emit_event(obj, "entity_delta", payload)
    elif entity.location:
        emit_event_room(entity.location, "entity_delta", payload)
    else:
        emit_event(entity, "entity_delta", payload)


def emit_combat_event(room, source, target, payload):
    emit_event_room(
        room,
        "combat_event",
        {"source_id": source.id if source else None, "target_id": target.id if target else None, **payload},
    )


def emit_vfx(room, vfx_id, source=None, target=None, extra=None):
    payload = {
        "vfx_id": vfx_id,
        "source_id": source.id if source else None,
        "target_id": target.id if target else None,
    }
    if extra:
        payload.update(extra)
    emit_event_room(room, "vfx_trigger", payload)
