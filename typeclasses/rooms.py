"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.safe_room = self.db.safe_room or False

    def get_display_exits(self, looker, **kwargs):
        """
        Get the 'exits' component of the object description. Called by `return_appearance`.
        """
        def _get_dir(ex):
            return ex.name

        exits = self.contents_get(exclude=looker)
        exits = [ex for ex in exits if ex.destination]
        if not exits:
            return ""

        exit_names = [f"|c{_get_dir(ex)}|n" for ex in exits]
        return f"|WObvious Exits:|n {', '.join(exit_names)}"


class GridRoom(Room):
    """
    A room that supports coordinate tracking and terrain types.
    """
    def at_object_creation(self):
        super().at_object_creation()
        # Default spatial coordinates within the room's grid (if applicable)
        # or the room's absolute world coordinates.
        self.db.coords = (0, 0, 0)
        self.db.terrain = "plain"
