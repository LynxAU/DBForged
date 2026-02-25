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
    
    # Gather form information
    active_form = entity.db.active_form
    form_mastery = entity.db.form_mastery or {}
    unlocked_forms = entity.db.unlocked_forms or []
    form_strain = getattr(entity.db, 'form_strain', 0)
    
    # Gather Android heat
    race = (entity.db.race or "").lower()
    android_heat = getattr(entity.db, 'android_heat', 0) if race == "android" else None
    
    # Gather limb states
    limbs = entity.db.limbs or {}
    limb_states = {k: v.get("state", "intact") for k, v in limbs.items()}
    has_limb_damage = any(s in ["damaged", "broken", "lost"] for s in limb_states.values())
    
    # Gather combo info
    combo_count = getattr(entity.db, 'combo_count', 0) or 0
    
    # Gather economy
    zeni = getattr(entity.db, 'zeni', 1000) or 1000
    dragon_balls = getattr(entity.db, 'dragon_balls', []) or []
    
    # Gather Zenkai boost
    zenkai_active = entity.has_status("zenkai_boost")
    zenkai_bonus = entity.get_status_data("zenkai_boost", {}).get("pl_bonus", 1.0) if zenkai_active else 1.0
    zenkai_count = getattr(entity.db, 'zenkai_count', 0) or 0
    
    # Get current form details if active
    form_info = None
    if active_form:
        from world.forms import FORMS
        form_data = FORMS.get(active_form, {})
        mastery = form_mastery.get(active_form, 0)
        from world.forms import get_form_tick_drain
        drain, _ = get_form_tick_drain(entity, active_form)
        form_info = {
            "key": active_form,
            "name": form_data.get("name", active_form),
            "mastery": mastery,
            "drain_tick": drain,
            "visuals": form_data.get("visuals", {}),
        }
    
    return {
        "hp": max(0, entity.db.hp_current or 0),
        "hp_max": hp_max,
        "ki": max(0, entity.db.ki_current or 0),
        "ki_max": ki_max,
        "pl": current_pl,
        "displayed_pl": breakdown.get("displayed_pl", current_pl),
        "active_form": active_form,
        "form_info": form_info,
        "unlocked_forms": unlocked_forms,
        "form_mastery": form_mastery,
        "form_strain": form_strain,
        "android_heat": android_heat,
        "zenkai_active": zenkai_active,
        "zenkai_bonus": zenkai_bonus,
        "zenkai_count": zenkai_count,
        "limbs": limb_states,
        "has_limb_damage": has_limb_damage,
        "combo": combo_count,
        "zeni": zeni,
        "dragon_balls": dragon_balls,
        "dragon_balls_collected": len(dragon_balls),
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
    room.msg_contents(text="", dbforged_event=packet, exclude=exclude or [])


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
    
    # Full stats for self (for HUD updates)
    payload_self = {
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
    
    # Limited stats for observers (no HP/KI disclosure)
    # This prevents metagaming by seeing exact health values
    payload_observer = {
        "entity": {
            "id": entity.id,
            "name": entity.key,
            "room": entity.location.id if entity.location else None,
            "room_name": entity.location.key if entity.location else None,
            "position": {"x": coords[0], "y": coords[1], "layer": coords[2]},
            "sprite_id": entity.db.sprite_id or "sprite_humanoid_default",
            "appearance": appearance,
            # Only send visible info - no exact HP/KI
            "active_form": stats.get("active_form"),
            "form_info": stats.get("form_info"),
            "displayed_pl": stats.get("displayed_pl"),  # Suppressed PL only
            "unlocked_forms": stats.get("unlocked_forms", []),
            "form_mastery": stats.get("form_mastery", {}),
            "zenkai_active": stats.get("zenkai_active"),
            "zenkai_count": stats.get("zenkai_count"),
            # Note: HP/KI intentionally omitted for observers
        }
    }
    
    # Broadcast to observers
    if recipients:
        for obj in recipients:
            # Determine if this is the entity itself or an observer
            if obj == entity:
                emit_event(obj, "entity_delta", payload_self)
            else:
                emit_event(obj, "entity_delta", payload_observer)
    elif entity.location:
        # Room broadcast - send full to self, limited to others
        emit_event(entity, "entity_delta", payload_self)
        emit_event_room(entity.location, "entity_delta", payload_observer, exclude=[entity])
    else:
        emit_event(entity, "entity_delta", payload_self)

    # Also send a direct self-only packet for client HUD updates.
    emit_event(entity, "player_frame", payload_self)


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
