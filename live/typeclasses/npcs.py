"""
Test Combat NPC - Configurable combat test dummy.

Supports configurable PL, stats, techniques, and AI behavior
for validating combat system against spec requirements.
"""

from __future__ import annotations

import random
import time

from evennia import create_object
from evennia.objects.objects import DefaultCharacter

from typeclasses.characters import Character
from world.combat import engage
from world.techniques import TECHNIQUES


class TestCombatNPC(Character):
    """
    Configurable test NPC for combat validation.
    
    Configurable attributes:
    - base_power: Base power level
    - strength, speed, balance, mastery, ki_control: Stats
    - hp_max, ki_max: Resources
    - test_ai: AI behavior mode (passive, aggressive, charging, teknik)
    - attack_interval: Seconds between AI actions
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("puppet:false()")
        self.db.is_npc = True
        self.db.is_test_dummy = True
        self.db.chargen_complete = True
        self.db.npc_role = "test_combat"
        self.db.sprite_id = "npc_test_dummy"
        
        # Default test configuration
        self.db.test_ai = "passive"  # passive, aggressive, charging, teknik
        self.db.attack_interval = 3.0  # seconds between actions
        self.db.last_action_time = 0
        
        # Default stats (level 10 balanced)
        self.db.base_power = 220
        self.db.strength = 15
        self.db.speed = 15
        self.db.balance = 14
        self.db.mastery = 14
        self.db.ki_control = 9
        
        # Default resources
        self.db.hp_max = 200
        self.db.hp_current = self.db.hp_max
        self.db.ki_max = 150
        self.db.ki_current = int(self.db.ki_max * 0.8)
        
        # Default techniques
        self.db.known_techniques = ["ki_blast", "kame_wave", "guard"]
        self.db.equipped_techniques = ["ki_blast", "guard"]

    def configure_test(self, **kwargs):
        """
        Configure this test NPC for a specific scenario.
        
        Usage:
            npc.configure_test(base_power=1000, strength=20, test_ai="aggressive")
        """
        for key, value in kwargs.items():
            if key in ("base_power", "strength", "speed", "balance", "mastery", 
                       "ki_control", "hp_max", "ki_max", "test_ai", "attack_interval"):
                setattr(self.db, key, value)
        
        # Recalculate derived values
        if "hp_max" in kwargs:
            self.db.hp_current = self.db.hp_max
        if "ki_max" in kwargs:
            self.db.ki_current = int(self.db.ki_max * 0.8)
            
        # Update techniques if specified
        if "techniques" in kwargs:
            self.db.known_techniques = kwargs["techniques"]
            self.db.equipped_techniques = kwargs["techniques"][:4]
        
        return self

    def get_test_info(self):
        """Return diagnostic info for testing."""
        pl, breakdown = self.get_current_pl()
        return {
            "name": self.key,
            "pl": pl,
            "hp": f"{self.db.hp_current}/{self.db.hp_max}",
            "ki": f"{self.db.ki_current}/{self.db.ki_max}",
            "ai": self.db.test_ai,
            "stats": {
                "strength": self.db.strength,
                "speed": self.db.speed,
                "balance": self.db.balance,
                "mastery": self.db.mastery,
                "ki_control": self.db.ki_control,
            },
            "breakdown": breakdown,
        }

    def at_tick(self):
        """Called by combat handler each tick."""
        self.run_test_ai()

    def run_test_ai(self):
        """Execute AI behavior based on test_ai mode."""
        now = time.time()
        if now - self.db.last_action_time < self.db.attack_interval:
            return
            
        self.db.last_action_time = now
        
        # Get combat target
        target_id = self.db.combat_target
        if not target_id:
            return
            
        from evennia.objects.models import ObjectDB
        target = ObjectDB.objects.filter(id=target_id).first()
        if not target or target.location != self.location:
            return
        
        ai_mode = self.db.test_ai
        
        if ai_mode == "passive":
            # Do nothing - just take hits
            pass
            
        elif ai_mode == "aggressive":
            # Attack with ki_blast
            self.execute_technique("ki_blast", target)
            
        elif ai_mode == "charging":
            # Try to charge if not already
            if not self.db.is_charging:
                from world.combat import start_charging
                start_charging(self, duration=10)
            else:
                self.execute_technique("ki_blast", target)
                
        elif ai_mode == "teknik":
            # Use random technique
            import random
            tech = random.choice(self.db.equipped_techniques)
            self.execute_technique(tech, target)

    def execute_technique(self, tech_key, target):
        """Execute a technique on target."""
        tech = TECHNIQUES.get(tech_key)
        if not tech:
            return False
            
        # Check Ki
        if not self.spend_ki(tech.get("ki_cost", 10)):
            return False
            
        # Check cooldown
        now = time.time()
        cooldowns = self.db.tech_cooldowns or {}
        if cooldowns.get(tech_key, 0) > now:
            return False
            
        # Set cooldown
        cooldown = tech.get("cooldown", 2.0)
        cooldowns[tech_key] = now + cooldown
        self.db.tech_cooldowns = cooldowns
        
        # Apply effect
        if "scaling" in tech:
            # Damage technique
            from world.power import compute_current_pl, pl_gap_effect
            a_pl, _ = compute_current_pl(self)
            d_pl, _ = compute_current_pl(target)
            gap = pl_gap_effect(a_pl, d_pl)
            
            scaling = tech["scaling"]
            base_damage = (
                scaling["base"]
                + int((self.db.strength or 10) * scaling["strength"])
                + int((self.db.mastery or 10) * scaling["mastery"])
                + int(a_pl * scaling["pl"])
            )
            damage = int(base_damage * gap["damage_mult"])
            
            target.apply_damage(damage, source=self, kind="technique")
            self.location.msg_contents(
                f"|c{tech['name']}|n from {self.key} hits {target.key} for |r{damage}|n!"
            )
            
        elif "effect" in tech:
            # Utility technique
            effect = tech["effect"]
            effect_type = effect.get("type")
            duration = effect.get("duration", 3.0)
            
            if effect_type == "stun":
                target.add_status("stunned", duration)
                self.location.msg_contents(
                    f"|c{tech['name']}|n from {self.key} stuns {target.key}!"
                )
            elif effect_type == "guard":
                self.add_status("guard", duration, reduction=effect.get("reduction", 0.45))
                self.location.msg_contents(f"{self.key} raises a |cguard|n!")
            elif effect_type == "afterimage":
                self.add_status("afterimage", duration)
                self.location.msg_contents(f"{self.key} vanishes into an |yafterimage|n!")
        
        return True


# Pre-configured test NPC templates
TEST_NPC_TEMPLATES = {
    # Basic even match (level 10 balanced)
    "test_even": {
        "base_power": 220,
        "strength": 15,
        "speed": 15,
        "balance": 14,
        "mastery": 14,
        "ki_control": 9,
        "hp_max": 200,
        "ki_max": 150,
        "test_ai": "aggressive",
        "attack_interval": 2.5,
    },
    
    # Weak opponent (for PL gap testing)
    "test_weak": {
        "base_power": 100,
        "strength": 8,
        "speed": 8,
        "balance": 8,
        "mastery": 8,
        "ki_control": 4,
        "hp_max": 80,
        "ki_max": 60,
        "test_ai": "passive",
        "attack_interval": 999,
    },
    
    # Strong opponent (for PL gap testing)  
    "test_strong": {
        "base_power": 1000,
        "strength": 35,
        "speed": 30,
        "balance": 28,
        "mastery": 30,
        "ki_control": 20,
        "hp_max": 800,
        "ki_max": 600,
        "test_ai": "aggressive",
        "attack_interval": 2.0,
    },
    
    # Overwhelming opponent (5000+ PL)
    "test_overwhelming": {
        "base_power": 5000,
        "strength": 60,
        "speed": 55,
        "balance": 50,
        "mastery": 55,
        "ki_control": 40,
        "hp_max": 4000,
        "ki_max": 3000,
        "test_ai": "aggressive",
        "attack_interval": 1.5,
    },
    
    # Charging test NPC
    "test_charger": {
        "base_power": 220,
        "strength": 15,
        "speed": 15,
        "balance": 14,
        "mastery": 14,
        "ki_control": 15,  # High ki control for faster charging
        "hp_max": 200,
        "ki_max": 200,
        "test_ai": "charging",
        "attack_interval": 1.0,
    },
    
    # Technique test NPC
    "test_teknik": {
        "base_power": 300,
        "strength": 20,
        "speed": 18,
        "balance": 15,
        "mastery": 20,
        "ki_control": 12,
        "hp_max": 250,
        "ki_max": 200,
        "test_ai": "teknik",
        "attack_interval": 4.0,
        "techniques": ["ki_blast", "kame_wave", "solar_flare", "guard", "afterimage_dash"],
    },
}


def create_test_npc(location, template_key="test_even", name=None):
    """
    Create a pre-configured test NPC.
    
    Args:
        location: Where to spawn the NPC
        template_key: Name of template from TEST_NPC_TEMPLATES
        name: Optional custom name
        
    Returns:
        TestCombatNPC instance
    """
    template = TEST_NPC_TEMPLATES.get(template_key, TEST_NPC_TEMPLATES["test_even"])
    
    npc = create_object(
        "typeclasses.npcs.TestCombatNPC",
        key=name or f"Test_{template_key}",
        location=location,
    )
    
    npc.configure_test(**template)
    return npc
