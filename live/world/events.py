"""
Structured JSON event emission for future sprite clients.
"""

from __future__ import annotations

import json
import time

from django.conf import settings

EVENT_PREFIX = "@event "


def _client_events_enabled():
    return bool(getattr(settings, "DBFORGED_EMIT_CLIENT_EVENTS", False))


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
    if not _client_events_enabled():
        return
    packet = {"type": event_type, "ts": round(time.time(), 3), **payload}
    receiver.msg(dbforged_event=packet)


def emit_event_room(room, event_type, payload, exclude=None):
    if not _client_events_enabled():
        return
    packet = {"type": event_type, "ts": round(time.time(), 3), **payload}
    room.msg_contents(dbforged_event=packet, exclude=exclude or [])


def emit_entity_delta(entity, recipients=None):
    stats = _safe_stats(entity)
    appearance = {
        "race": entity.db.race or "unknown",
        "sex": entity.db.sex or "other",
        "hair_style": entity.db.hair_style or "spiky",
        "hair_color": entity.db.hair_color or "black",
        "eye_color": entity.db.eye_color or "black",
        "aura_color": entity.db.aura_color or "white",
    }
    coords = getattr(entity.db, "coords", (0, 0, 0))
    if coords is None:
        coords = (0, 0, 0)
    payload = {
        "entity": {
            "id": entity.id,
            "name": entity.key,
            "room": entity.location.id if entity.location else None,
            "room_name": entity.location.key if entity.location else None,
            "position": {"x": coords[0], "y": coords[1], "layer": coords[2]},
            "sprite_id": entity.db.sprite_id or "sprite_humanoid_default",
            "appearance": appearance,
            **stats,
        }
    }
    
    # Broadcast to observers
    if recipients:
        for obj in recipients:
            emit_event(obj, "entity_delta", payload)
    elif entity.location:
        emit_event_room(entity.location, "entity_delta", payload)
    else:
        emit_event(entity, "entity_delta", payload)

    # Also send a direct self-only packet for client HUD updates.
    emit_event(entity, "player_frame", payload)


def emit_map_data(player, center_x, center_y, radius=15):
    """
    Sends a serialized grid of terrain data to the player.
    """
    from evennia.objects.models import ObjectDB
    # Fetch GridRooms in the box
    candidates = ObjectDB.objects.filter(db_typeclass_path__contains="GridRoom")
    grid = []
    player_coords = player.db.coords
    z = player_coords[2] if player_coords and len(player_coords) > 2 else 0
    
    for r in candidates:
        rc = r.db.coords
        if rc is None:
            continue
        if rc and rc[2] == z and abs(rc[0] - center_x) <= radius and abs(rc[1] - center_y) <= radius:
            grid.append({
                "x": rc[0],
                "y": rc[1],
                "terrain": r.db.terrain or "plain"
            })
    
    payload = {
        "center_x": center_x,
        "center_y": center_y,
        "radius": radius,
        "grid": grid
    }
    emit_event(player, "map_data", payload)


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
