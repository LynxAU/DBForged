"""
NPC typeclasses for DB vertical slice.
"""

from typeclasses.characters import Character
from world.npc_content import get_npc_definition
from world.quests import get_quests_for_npc


class DBNPC(Character):
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("puppet:false()")
        self.db.is_npc = True
        self.db.chargen_complete = True
        self.db.known_techniques = ["ki_blast", "guard"]
        self.db.equipped_techniques = ["ki_blast", "guard"]
        self.db.npc_content_key = self.db.npc_content_key or None


class TrainingNPC(DBNPC):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.npc_role = "trainer"
        self.db.sprite_id = self.db.sprite_id or "npc_trainer"
        self.db.trainer_key = self.db.trainer_key or self.db.npc_content_key

    def get_content_definition(self):
        key = self.db.trainer_key or self.db.npc_content_key
        return get_npc_definition(key) if key else None

    def get_dialogue_lines(self):
        data = self.get_content_definition()
        return list((data or {}).get("dialogue", []) or (self.db.dialogue_lines or []))

    def get_quest_hooks(self):
        key = self.db.trainer_key or self.db.npc_content_key
        return get_quests_for_npc(key) if key else []

    def get_trainer_rewards(self):
        data = self.get_content_definition() or {}
        return data.get("trainer_rewards", {})


class HostileNPC(DBNPC):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.npc_role = "hostile"
        self.db.sprite_id = self.db.sprite_id or "npc_hostile"
