"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""


def at_initial_setup():
    from evennia import create_script
    from evennia.scripts.models import ScriptDB
    from evennia.utils import logger

    from world.db_init import build_vertical_slice_world
    from world.build_kame_island import build_kame_island

    # ── Validate registries before building the world ──────────────────────
    from world.techniques import validate_technique_registry
    from world.forms      import validate_form_registry
    from world.racials    import validate_racial_registry

    errors = []
    errors += validate_technique_registry() or []
    errors += validate_form_registry()       or []
    errors += validate_racial_registry()     or []

    if errors:
        for err in errors:
            logger.log_err(f"[Registry] {err}")
        logger.log_warn(f"[Registry] {len(errors)} validation error(s) found — check logs before launch.")
    else:
        logger.log_info("[Registry] All registries validated OK.")

    # Build the initial world
    earth_plains = build_vertical_slice_world()
    
    # Build Kame Island
    kame_island = build_kame_island()
    
    # Add connection from Earth Plains to Kame Island (boat ride)
    from evennia.objects.models import ObjectDB
    from evennia.utils.create import create_object
    
    # Find the boat/sign at Earth Plains that leads to Kame Island
    existing_exit = ObjectDB.objects.filter(
        db_key__iexact="boat", 
        db_location=earth_plains,
        db_typeclass_path="typeclasses.exits.Exit"
    ).first()
    
    if not existing_exit:
        # Create a boat/teleport to Kame Island
        kame_beach = ObjectDB.objects.filter(
            db_key__iexact="Kame Island: Beach Shore",
            db_typeclass_path="typeclasses.rooms.Room"
        ).first()
        
        if kame_beach and earth_plains:
            boat_exit = create_object(
                "typeclasses.exits.Exit",
                key="boat",
                location=earth_plains,
                destination=kame_beach,
            )
            boat_exit.aliases.add("kame")
            boat_exit.aliases.add("island")
            boat_exit.db.desc = "A small boat that can take you to Kame Island!"
            print("✓ Added boat to Kame Island from Earth Plains")
    
    # Add connection from Kame Island back to Earth Plains (boat ride)
    kame_dock = ObjectDB.objects.filter(
        db_key__iexact="Kame Island: Small Dock",
        db_typeclass_path="typeclasses.rooms.Room"
    ).first()
    
    existing_return = ObjectDB.objects.filter(
        db_key__iexact="boat",
        db_location=kame_dock,
        db_typeclass_path="typeclasses.exits.Exit"
    ).first()
    
    if not existing_return and kame_dock and earth_plains:
        return_boat = create_object(
            "typeclasses.exits.Exit",
            key="boat",
            location=kame_dock,
            destination=earth_plains,
        )
        return_boat.aliases.add("boat")
        return_boat.aliases.add("earth")
        return_boat.aliases.add("mainland")
        return_boat.db.desc = "A small boat that can take you back to Earth!"
        print("✓ Added boat to Earth from Kame Island")
    
    exists = ScriptDB.objects.filter(db_key="db_combat").first()
    if not exists:
        create_script("world.combat.CombatHandler")
