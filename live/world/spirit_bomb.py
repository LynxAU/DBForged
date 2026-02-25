"""
Spirit Bomb System - DBForged Bible Implementation
====================================================
Implements Spirit Bomb charge, damage calculation, interrupt mechanic, and AoE effects.
"""

from evennia import DefaultScript
import random


class SpiritBomb:
    """
    Manages Spirit Bomb charge and release mechanics.
    """
    
    def __init__(self, caster, charge_duration=0):
        self.caster = caster
        self.charge_start_time = charge_duration
        self.is_charging = False
        self.is_ready = False
        self.charge_messages = [
            "{caster} begins gathering energy...",
            "{caster}'s aura flares wildly as more energy flows into the orb!",
            "The Spirit Bomb grows larger, pulsing with deadly light!",
            "{caster} struggles to contain the massive energy!",
            "The Spirit Bomb is fully charged! {caster} can release it now!",
        ]
        self.interrupted = False
        
    def start_charge(self):
        """Initiate Spirit Bomb charging."""
        self.is_charging = True
        self.charge_start_time = 0
        self.caster.msg("|rYou begin gathering energy for a Spirit Bomb...|n")
        
    def update_charge(self, current_time):
        """Update charge status and return charge stage (0-4)."""
        if not self.is_charging:
            return -1
            
        elapsed = current_time - self.charge_start_time
        stage = min(int(elapsed / 6), 4)  # 0-4 based on 30s max charge
        return stage
        
    def get_charge_message(self, stage):
        """Get the message for the current charge stage."""
        if 0 <= stage < len(self.charge_messages):
            msg = self.charge_messages[stage]
            return msg.format(caster=self.caster.key)
        return ""
        
    def calculate_damage(self, charge_time):
        """
        Calculate Spirit Bomb damage based on charge time.
        Base: PL * 0.5 * (charge_time / 10)
        Max (30s): PL * 1.5
        """
        base_pl = self.caster.db.power_level or 100
        multiplier = min(charge_time / 10.0, 3.0)  # 0.1 to 3.0
        damage = int(base_pl * 0.5 * multiplier)
        return max(damage, 10)  # Minimum 10 damage
        
    def release(self):
        """Release the Spirit Bomb as an AoE attack."""
        if not self.is_charging:
            return None
            
        charge_time = 0  # Will be calculated from elapsed time
        damage = self.calculate_damage(charge_time)
        
        # Get all targets in the room
        targets = []
        if self.caster.location:
            for obj in self.caster.location.contents:
                if obj != self.caster and hasattr(obj, 'db'):
                    if hasattr(obj, 'take_damage'):
                        targets.append(obj)
        
        # Apply damage to all targets
        results = {
            'damage': damage,
            'targets': [],
            'caster': self.caster.key
        }
        
        for target in targets:
            # Check if target can be affected (not immune)
            if not hasattr(target, 'is_invulnerable') or not target.is_invulnerable:
                if hasattr(target, 'take_damage'):
                    actual_damage = target.take_damage(damage, 'spirit_bomb')
                    results['targets'].append({
                        'name': target.key,
                        'damage': actual_damage
                    })
        
        self.is_charging = False
        self.is_ready = False
        
        return results
        
    def interrupt(self):
        """Handle interrupt - caster takes damage."""
        if not self.is_charging:
            return None
            
        # Caster takes 25% of potential max damage
        potential_damage = self.calculate_damage(30)
        self_damage = int(potential_damage * 0.25)
        
        if hasattr(self.caster, 'take_damage'):
            actual = self.caster.take_damage(self_damage, 'spirit_bomb_fail')
        
        self.is_charging = False
        self.interrupted = True
        
        return {
            'self_damage': actual,
            'caster': self.caster.key
        }
        
    def get_charge_percentage(self, current_time):
        """Get charge as percentage (0-100)."""
        if not self.is_charging:
            return 0
        elapsed = current_time - self.charge_start_time
        return min(int((elapsed / 30.0) * 100), 100)


class FlurryAttack:
    """
    Implements Flurry Attack - rapid strikes at reduced damage.
    """
    
    # Flurry damage is 50% of normal per strike
    FLURRY_DAMAGE_PERCENT = 0.5
    
    # Number of strikes in a flurry
    MIN_STRIKES = 3
    MAX_STRIKES = 5
    
    # Chance to trigger flurry in combat
    FLURRY_TRIGGER_CHANCE = 0.15  # 15% chance
    
    @staticmethod
    def can_trigger(attacker):
        """Check if attacker can trigger a flurry attack."""
        # Must have some technique skill
        technique_level = attacker.db.technique_level or 0
        return technique_level >= 5
        
    @staticmethod
    def calculate_strikes():
        """Calculate number of strikes in the flurry."""
        return random.randint(FlurryAttack.MIN_STRIKES, FlurryAttack.MAX_STRIKES)
        
    @staticmethod
    def execute(attacker, target, base_damage):
        """
        Execute a flurry attack against target.
        Returns dict with results of each strike.
        """
        if not hasattr(target, 'take_damage'):
            return None
            
        num_strikes = FlurryAttack.calculate_strikes()
        strike_damage = int(base_damage * FlurryAttack.FLURRY_DAMAGE_PERCENT)
        
        results = {
            'is_flurry': True,
            'num_strikes': num_strikes,
            'strike_damage': strike_damage,
            'total_damage': 0,
            'hits': 0,
            'misses': 0,
            'messages': []
        }
        
        for i in range(num_strikes):
            # 80% hit chance per strike
            if random.random() < 0.8:
                actual = target.take_damage(strike_damage, 'flurry')
                results['hits'] += 1
                results['total_damage'] += actual
                results['messages'].append(f"Strike {i+1} hits for {actual} damage!")
            else:
                results['misses'] += 1
                results['messages'].append(f"Strike {i+1} misses!")
                
        return results
        
    @staticmethod
    def should_trigger():
        """Randomly determine if flurry should trigger."""
        return random.random() < FlurryAttack.FLURRY_TRIGGER_CHANCE


# Global storage for active spirit bombs
_active_spirit_bombs = {}


def get_spirit_bomb(caller):
    """Get or create a spirit bomb for the caller."""
    caller_id = caller.id
    if caller_id not in _active_spirit_bombs:
        _active_spirit_bombs[caller_id] = SpiritBomb(caster=caller)
    return _active_spirit_bombs[caller_id]


def clear_spirit_bomb(caller):
    """Clear the spirit bomb for the caller."""
    caller_id = caller.id
    if caller_id in _active_spirit_bombs:
        del _active_spirit_bombs[caller_id]
