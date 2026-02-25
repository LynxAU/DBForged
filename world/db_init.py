"""
One-time world bootstrap for the DB vertical slice.
"""

from evennia.objects.models import ObjectDB
from evennia.utils.create import create_object


def _get_room(key):
    return ObjectDB.objects.filter(db_key__iexact=key, db_typeclass_path="typeclasses.rooms.Room").first()


def _get_or_create_room(key, desc, safe=False):
    room = _get_room(key)
    if room:
        return room
    room = create_object("typeclasses.rooms.Room", key=key)
    room.db.desc = desc
    room.db.safe_room = bool(safe)
    if safe:
        room.tags.add("safe_room", category="zone")
    return room


def _create_exit_if_missing(key, location, destination, aliases=None):
    existing = ObjectDB.objects.filter(
        db_key__iexact=key, db_typeclass_path="typeclasses.exits.Exit", db_location=location
    ).first()
    if existing:
        return existing
    return create_object(
        "typeclasses.exits.Exit",
        key=key,
        location=location,
        destination=destination,
        aliases=aliases or [],
    )


def _get_or_create_npc(key, typeclass, location, desc, attrs=None):
    npc = ObjectDB.objects.filter(db_key__iexact=key, db_typeclass_path=typeclass).first()
    if npc:
        npc.location = location
        npc.db.desc = desc
        return npc
    npc = create_object(typeclass, key=key, location=location)
    npc.db.desc = desc
    for attr_key, attr_value in (attrs or {}).items():
        setattr(npc.db, attr_key, attr_value)
    return npc


def build_vertical_slice_world():
    plains_camp = _get_or_create_room(
        "Earth: Plains - Safe Camp",
        "A quiet grassland camp with flattened stones for sparring. This is a safe recovery point.",
        safe=True,
    )
    plains_pass = _get_or_create_room(
        "Earth: Plains - Rocky Pass",
        "Tall grasses bend in the wind between broken cliffs. The terrain invites fast movement drills.",
    )
    city_gate = _get_or_create_room(
        "Earth: City Outskirts - Gate",
        "Dusty roads converge near old concrete barriers. Traders pass while fighters test each other.",
    )
    city_alley = _get_or_create_room(
        "Earth: City Outskirts - Alley",
        "A cramped alley with cracked walls and scorched marks from stray ki blasts.",
    )

    _create_exit_if_missing("east", plains_camp, plains_pass, aliases=["e"])
    _create_exit_if_missing("west", plains_pass, plains_camp, aliases=["w"])
    _create_exit_if_missing("east", plains_pass, city_gate, aliases=["e"])
    _create_exit_if_missing("west", city_gate, plains_pass, aliases=["w"])
    _create_exit_if_missing("south", city_gate, city_alley, aliases=["s"])
    _create_exit_if_missing("north", city_alley, city_gate, aliases=["n"])

    _get_or_create_npc(
        "Master Rokan",
        "typeclasses.npcs.TrainingNPC",
        plains_camp,
        "A patient martial arts mentor with a battered scouter and strict fundamentals.",
        attrs={
            "race": "human",
            "base_power": 190,
            "sprite_id": "npc_master_rokan",
            "strength": 14,
            "speed": 13,
            "balance": 14,
            "mastery": 18,
            "ki_control": 22,
            "npc_role": "trainer",
            "trainer_key": "master_rokan",
            "npc_content_key": "master_rokan",
        },
    )
    _get_or_create_npc(
        "Bandit Raider",
        "typeclasses.npcs.HostileNPC",
        city_alley,
        "A volatile raider radiating unstable ki and picking fights with anyone entering the alley.",
        attrs={
            "race": "human",
            "base_power": 145,
            "sprite_id": "npc_bandit_raider",
            "strength": 12,
            "speed": 11,
            "balance": 9,
            "mastery": 8,
            "ki_control": 4,
        },
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # FIRST FIGHT - Training Dummy in the safe camp for instant action!
    # ═══════════════════════════════════════════════════════════════════════
    _get_or_create_npc(
        "Training Dummy",
        "typeclasses.npcs.HostileNPC",
        plains_camp,
        "A battered training dummy used for sparring practice. It's covered in scorch marks and dented armor plating. Perfect for beginners!",
        attrs={
            "race": "android",
            "base_power": 60,  # Weak enough for new players to beat!
            "sprite_id": "npc_training_dummy",
            "strength": 8,
            "speed": 5,
            "balance": 8,
            "mastery": 1,
            "ki_control": 1,
            "npc_role": "sparring",
            "aggressive": False,  # Won't attack first
        },
    )
    
    return plains_camp
