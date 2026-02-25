"""
Beam Clash System - DBZ-style beam struggles.

When two beam attacks collide, initiates a beam clash where players
push energy to try to overwhelm their opponent.
"""

from __future__ import annotations

import time
import random


class BeamClash:
    """
    Manages a beam clash between two characters.
    
    Position ranges from 0 (p1 wins) to 100 (p2 wins), starting at 50.
    """
    
    def __init__(self, p1, p2, room):
        self.p1 = p1
        self.p2 = p2
        self.room = room
        self.position = 50
        self.p1_energy = 0
        self.p2_energy = 0
        self.start_time = time.time()
        self.last_update = time.time()
        
        # Track active clashes for cleanup
        self._register()
    
    def _register(self):
        """Register this clash in the room for tracking."""
        if not hasattr(self.room, 'beam_clash'):
            self.room.beam_clash = None
        self.room.beam_clash = self
    
    def _unregister(self):
        """Unregister this clash."""
        if hasattr(self.room, 'beam_clash') and self.room.beam_clash == self:
            self.room.beam_clash = None
    
    def push(self, player, timing_bonus: int = 0) -> str:
        """
        Player pushes energy into the beam clash.
        
        Returns:
            "p1_wins", "p2_wins", or "continuing"
        """
        # Calculate base push
        base_push = 10
        push_amount = base_push + timing_bonus + random.randint(-2, 2)
        
        if player == self.p1:
            self.p1_energy += push_amount
        elif player == self.p2:
            self.p2_energy += push_amount
        else:
            return "continuing"  # Invalid player
        
        # Compare energies and adjust position
        if self.p1_energy > self.p2_energy:
            self.position -= 5
        elif self.p2_energy > self.p1_energy:
            self.position += 5
        else:
            # Tie - small random drift
            if random.random() < 0.5:
                self.position -= 1
            else:
                self.position += 1
        
        # Clamp position
        self.position = max(0, min(100, self.position))
        
        # Check for resolution
        if self.position <= 0:
            return "p1_wins"
        elif self.position >= 100:
            return "p2_wins"
        
        return "continuing"
    
    def update(self):
        """
        Update beam clash state - called every tick.
        Decays position toward center if no input.
        """
        now = time.time()
        if now - self.last_update < 1.0:
            return  # Only update once per second
        
        self.last_update = now
        
        # Decay toward center (50)
        if self.position < 45:
            self.position += 1
        elif self.position > 55:
            self.position -= 1
        
        # Small energy decay to prevent infinite accumulation
        self.p1_energy = max(0, self.p1_energy - 2)
        self.p2_energy = max(0, self.p2_energy - 2)
    
    def get_position_display(self) -> str:
        """
        Get visual representation of beam position.
        """
        # Create a visual bar
        bar_length = 20
        p1_pos = int((self.position / 100) * bar_length)
        p2_pos = bar_length - p1_pos
        
        bar = "=" * p1_pos + "O" + "=" * p2_pos
        
        return f"[{bar}] P1 <<<< >>>> P2"
    
    def resolve(self, winner, loser) -> dict:
        """
        Resolve the beam clash.
        
        Returns damage and effect data.
        """
        self._unregister()
        
        # Calculate damage based on how far the beam pushed
        push_distance = abs(50 - self.position)
        base_damage = 50 + (push_distance * 3)
        
        return {
            "winner": winner,
            "loser": loser,
            "base_damage": base_damage,
            "push_distance": push_distance,
            "duration": time.time() - self.start_time
        }
    
    def is_expired(self, max_duration: int = 60) -> bool:
        """Check if beam clash has lasted too long."""
        return (time.time() - self.start_time) > max_duration


def start_beam_clash(p1, p2, room):
    """
    Start a new beam clash between two characters.
    """
    # Check if clash already exists
    if hasattr(room, 'beam_clash') and room.beam_clash is not None:
        return None
    
    clash = BeamClash(p1, p2, room)
    return clash


def get_beam_clash(room):
    """
    Get the current beam clash in a room, if any.
    """
    if hasattr(room, 'beam_clash'):
        return room.beam_clash
    return None


def end_beam_clash(room):
    """
    End the current beam clash in a room.
    """
    if hasattr(room, 'beam_clash') and room.beam_clash is not None:
        room.beam_clash._unregister()
