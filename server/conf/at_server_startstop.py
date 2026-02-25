"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""


def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    pass


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Run content validation on startup to catch configuration errors
    _validate_content()
    
    # Initialize tournament persistence
    _init_tournament_persistence()


def _validate_content():
    """Validate game content on server startup."""
    try:
        from world.content_validation import validate_all_content, has_validation_errors
        result = validate_all_content()
        if has_validation_errors(result):
            print("WARNING: Content validation errors detected:")
            for category, errors in result.get("errors", {}).items():
                if errors:
                    print(f"  {category}: {errors}")
        else:
            print("Content validation passed.")
    except Exception as e:
        print(f"Content validation failed: {e}")


def _init_tournament_persistence():
    """Initialize tournament persistence on server startup."""
    try:
        from world.tournaments import _init_persistence
        _init_persistence()
        print("Tournament persistence initialized.")
    except Exception as e:
        print(f"Tournament persistence init failed: {e}")


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
