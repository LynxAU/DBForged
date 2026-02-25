"""
Mobility Systems - DBForged Bible Implementation
=================================================
Implements timeskip, teleport, and Instant Transmission.
"""

import time


def timeskip(character, target):
    """
    Teleport behind target (timeskip).
    Requires 50% of target's PL.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check if target is valid
    if not target or target.location != character.location:
        return False, "That target isn't here."
    
    # Check PL requirement (50% of target's PL)
    character_pl = character.db.power_level or 100
    target_pl = target.db.power_level or 100
    
    required_pl = target_pl * 0.5
    if character_pl < required_pl:
        return False, f"Your PL ({int(character_pl)}) is too low to timeskip to {target.key} (need {int(required_pl)})."
    
    # Check ki
    ki_cost = int(target_pl * 0.05)  # 5% of target's PL in KI
    current_ki = character.db.ki_current or 0
    if current_ki < ki_cost:
        return False, f"Not enough KI (need {ki_cost})."
    
    # Deduct KI
    character.db.ki_current = current_ki - ki_cost
    
    # Store original position for potential swap
    original_location = character.location
    original_position = character.position
    
    # Teleport behind target (swap positions)
    target_position = getattr(target, 'position', 'front')
    
    # Move character behind target
    character.location = target.location
    character.position = 'behind'
    target.position = 'front'
    
    return True, f"You vanish and appear behind {target.key}!"


def position_swap(character, target):
    """
    Swap positions with target.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not target or target.location != character.location:
        return False, "That target isn't here."
    
    # Simple swap - just move both to each other's location
    char_loc = character.location
    target_loc = target.location
    
    character.location = target_loc
    target.location = char_loc
    
    return True, f"You swap positions with {target.key}!"


def save_teleport_location(character, location_name):
    """
    Save a teleport location (lock).
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not location_name:
        return False, "Usage: teleport save <name>"
    
    # Store the location
    saved_locations = getattr(character.db, 'saved_locations', {})
    
    if character.location:
        saved_locations[location_name.lower()] = {
            'room_id': character.location.id,
            'room_name': character.location.key,
            'saved_at': time.time()
        }
        character.db.saved_locations = saved_locations
    
    return True, f"Location saved as '{location_name}'."


def teleport_to_location(character, location_name):
    """
    Teleport to a saved location.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    saved_locations = getattr(character.db, 'saved_locations', {})
    
    location = saved_locations.get(location_name.lower())
    if not location:
        return False, f"No saved location named '{location_name}'."
    
    # KI cost based on time since save
    time_since_save = time.time() - location['saved_at']
    ki_cost = max(10, int(time_since_save / 60))  # 10 KI minimum, +1 per minute
    
    current_ki = character.db.ki_current or 0
    if current_ki < ki_cost:
        return False, f"Not enough KI (need {ki_cost})."
    
    character.db.ki_current = current_ki - ki_cost
    
    # Find the room
    from evennia.objects.models import ObjectDB
    try:
        room = ObjectDB.objects.get(id=location['room_id'])
        character.location = room
        return True, f"You teleport to {location['room_name']}!"
    except:
        return False, "That location no longer exists."


def instant_transmission(character, target_name=None):
    """
    Instant Transmission - teleport to an ally.
    If no target specified, returns to last IT location.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check for last IT location
    last_it_location = getattr(character.db, 'last_it_location', None)
    
    if not target_name:
        # Return to last location
        if not last_it_location:
            return False, "No previous Instant Transmission location."
        
        from evennia.objects.models import ObjectDB
        try:
            room = ObjectDB.objects.get(id=last_it_location['room_id'])
            character.location = room
            return True, "You use Instant Transmission to return to your previous location!"
        except:
            return False, "That location no longer exists."
    
    # Find target ally
    if not character.location:
        return False, "You have no location."
    
    # Search for the ally in all rooms (expensive, but that's the mechanic)
    from evennia.objects.models import ObjectDB
    target = None
    
    for obj in ObjectDB.objects.all():
        if obj.key.lower() == target_name.lower() and hasattr(obj, 'db'):
            if getattr(obj.db, 'is_ally', False) or getattr(obj.db, 'account', None):
                target = obj
                break
    
    if not target:
        return False, f"Cannot find ally '{target_name}'."
    
    if not target.location:
        return False, f"{target.key} has no valid location."
    
    # Save current location before IT
    if character.location:
        character.db.last_it_location = {
            'room_id': character.location.id,
            'room_name': character.location.key,
            'saved_at': time.time()
        }
    
    # Teleport
    character.location = target.location
    
    return True, f"You use Instant Transmission to appear beside {target.key}!"


def get_saved_locations(character):
    """Get list of saved teleport locations."""
    saved = getattr(character.db, 'saved_locations', {})
    if not saved:
        return []
    
    lines = ["Saved locations:"]
    for name, data in saved.items():
        lines.append(f"  {name}: {data['room_name']}")
    
    return lines
