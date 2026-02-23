"""
Map and spatial utilities for the coordinate-based grid.

This module provides functions for scanning the spatial coordinate 
system, locating entities and rooms based on (X, Y, Z) coordinates,
and rendering ANSI map outputs for player feedback. Designed to be
used by zone builders and developers to query the active game world.
"""

from evennia.objects.models import ObjectDB
from evennia.utils.search import search_object

TERRAIN_MAP = {
    "plain": "|g.|n",
    "grass": "|G,|n",
    "sand": "|y.|n",
    "water": "|b≈|n",
    "mountain": "|x^|n",
    "floor": "|w.|n",
    "wall": "|X#|n",
}

def get_room_at(x, y, z=0):
    """
    Find a GridRoom at specific coordinates.

    Args:
        x (int): The X coordinate.
        y (int): The Y coordinate.
        z (int, optional): The Z coordinate (depth/elevation). Defaults to 0.

    Returns:
        GridRoom: The room object at the specified coordinates, or None if empty.

    Example:
        >>> room = get_room_at(10, -5, 0)
        >>> if room:
        ...     print(f"Room found with terrain {room.db.terrain}")
    """
    candidates = ObjectDB.objects.filter(db_typeclass_path__contains="GridRoom")
    for room in candidates:
        if room.db.coords == (x, y, z):
            return room
    return None

def get_entities_in_radius(x, y, radius, z=0):
    """
    Get all characters and NPCs within a specific radius of a focal point.

    Useful for spatial queries like AoE attacks or radar/scouting systems.

    Args:
        x (int): Center X coordinate.
        y (int): Center Y coordinate.
        radius (int): Maximum distance from the center point to search.
        z (int, optional): Target Z coordinate layer. Defaults to 0.

    Returns:
        list: A list of Character/NPC objects within the radius.

    Example:
        >>> nearby_targets = get_entities_in_radius(user_x, user_y, radius=5)
        >>> for target in nearby_targets:
        ...     target.msg("You are in range of an event!")
    """
    # For now, we fetch all Characters and NPCs (as they inherit from Character)
    # and filter by coordinates.
    from typeclasses.characters import Character
    
    entities = []
    # Using Evennia's ObjectDB to get all objects of the right typeclass
    # (In a real high-traffic MUD, you'd use a spatial cache or more precise Django filters)
    candidates = ObjectDB.objects.filter(db_typeclass_path__contains="Character")
    
    for obj in candidates:
        coords = obj.db.coords
        if coords and len(coords) >= 2:
            ox, oy = coords[0], coords[1]
            oz = coords[2] if len(coords) > 2 else 0
            if oz == z and (ox - x)**2 + (oy - y)**2 <= radius**2:
                entities.append(obj)
    return entities

def get_entity_token(obj, is_self=False):
    """
    Returns the ANSI token for an entity.
    """
    if is_self:
        return "|R@|n"
    role = obj.db.npc_role
    if role == "hostile":
        return "|ro|n"
    if role == "trainer":
        return "|m!|n"
    if obj.db.is_npc:
        return "|yi|n"
    return "|W@|n" # Other players

def render_map(center_x, center_y, radius=5, z=0, target_obj=None):
    """
    Builds a 2D string matrix of the map around a center point.

    Scans for all GridRooms within the bounding box defined by the radius,
    maps their terrain to ANSI colors, and overlays any entities in the region.

    Args:
        center_x (int): The X coordinate to center the map on.
        center_y (int): The Y coordinate to center the map on.
        radius (int, optional): Number of tiles in each direction to render. Defaults to 5.
        z (int, optional): The Z coordinate layer to render. Defaults to 0.
        target_obj (Object, optional): The entity to represent as "self" (|R@|n). Defaults to None.

    Returns:
        str: A multi-line string containing the colored ANSI map, ready to be sent to a player.

    Example:
        >>> ascii_map = render_map(player.db.coords[0], player.db.coords[1], target_obj=player)
        >>> player.msg(ascii_map)
    """
    # 1. Fetch all GridRooms in the bounding box
    candidates = ObjectDB.objects.filter(db_typeclass_path__contains="GridRoom")
    room_map = {}
    for r in candidates:
        rc = r.db.coords
        if rc and rc[2] == z and abs(rc[0] - center_x) <= radius and abs(rc[1] - center_y) <= radius:
            room_map[(rc[0], rc[1])] = r
            
    # 2. Fetch all entities in the radius
    entities = get_entities_in_radius(center_x, center_y, radius, z)
    entity_map = {}
    for e in entities:
        ec = e.db.coords
        if ec:
            pos = (ec[0], ec[1])
            if pos not in entity_map:
                entity_map[pos] = []
            entity_map[pos].append(e)

    # 3. Build the grid
    lines = []
    for y in range(center_y + radius, center_y - radius - 1, -1):
        row = []
        for x in range(center_x - radius, center_x + radius + 1):
            pos = (x, y)
            room = room_map.get(pos)
            
            # Terrain layer
            cell = TERRAIN_MAP.get(room.db.terrain if room else "plain", "|x |n")
            
            # Entity layer (topmost entity)
            if pos in entity_map:
                top_e = entity_map[pos][0]
                # If target_obj is among them, use self token
                is_self = target_obj in entity_map[pos]
                cell = get_entity_token(top_e, is_self)
                
            row.append(cell)
        lines.append(" ".join(row))
        
    return "\n".join(lines)
