"""
NPC typeclasses for DB vertical slice.
"""

from typeclasses.characters import Character


class DBNPC(Character):
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("puppet:false()")
        self.db.is_npc = True
        self.db.known_techniques = ["ki_blast", "guard"]
        self.db.equipped_techniques = ["ki_blast", "guard"]


class TrainingNPC(DBNPC):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.npc_role = "trainer"
        self.db.sprite_id = self.db.sprite_id or "npc_trainer"


class HostileNPC(DBNPC):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.npc_role = "hostile"
        self.db.sprite_id = self.db.sprite_id or "npc_hostile"
