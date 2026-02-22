#!/usr/bin/env python
"""
Direct API combat test - tests combat system using Evennia's internal API.
"""

import os
import sys
import time

# Set up Django environment - need to be in live/ directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

# Set PYTHONPATH for evennia
pythonpath = os.path.dirname(os.path.abspath(__file__))
if pythonpath not in sys.path:
    sys.path.insert(0, pythonpath)

from evennia import ObjectDB
from typeclasses.npcs import create_test_npc, TEST_NPC_TEMPLATES
from world.combat import engage, disengage, start_charging, stop_charging, register_beam
from world.power import compute_current_pl, pl_gap_effect
from world.techniques import TECHNIQUES
from world.forms import FORMS

def test_basic_combat():
    """Test 1: Basic combat between two evenly matched NPCs."""
    print("\n" + "="*60)
    print("TEST 1: BASIC COMBAT (Even Match)")
    print("="*60)
    
    # Get or create a test room
    room = ObjectDB.objects.filter(db_key__icontains="Combat Test").first()
    if not room:
        from evennia import create_object
        from evennia.objects.objects import DefaultRoom
        room = create_object(
            "typeclasses.rooms.Room",
            key="Combat Test Arena",
            location=None,
        )
        room.db.desc = "A dedicated combat testing arena."
    
    print(f"Using room: {room.key}")
    
    # Create two evenly-matched NPCs
    npc1 = create_test_npc(room, "test_even", "Attacker")
    npc2 = create_test_npc(room, "test_even", "Defender")
    
    # Get their PL
    pl1, _ = compute_current_pl(npc1)
    pl2, _ = compute_current_pl(npc2)
    
    print(f"\nAttacker PL: {pl1}")
    print(f"Defender PL: {pl2}")
    print(f"HP: {npc1.db.hp_current}/{npc1.db.hp_max} vs {npc2.db.hp_current}/{npc2.db.hp_max}")
    print(f"Ki: {npc1.db.ki_current}/{npc1.db.ki_max} vs {npc2.db.ki_current}/{npc2.db.ki_max}")
    
    # Engage in combat
    engage(npc1, npc2)
    print(f"\n*** {npc1.key} and {npc2.key} engaged in combat! ***")
    
    # Let combat run for a few seconds
    print("\n--- Combat in progress (5 seconds) ---")
    for i in range(5):
        time.sleep(1)
        print(f"  Tick {i+1}: {npc1.key} HP={npc1.db.hp_current}, {npc2.key} HP={npc2.db.hp_current}")
    
    # Disengage and show results
    disengage(npc1)
    disengage(npc2)
    
    print(f"\n--- Results ---")
    print(f"{npc1.key} HP: {npc1.db.hp_current}/{npc1.db.hp_max}")
    print(f"{npc2.key} HP: {npc2.db.hp_current}/{npc2.db.hp_max}")
    
    # Cleanup
    npc1.delete()
    npc2.delete()
    print("\nTest complete!")

def test_beam_battle():
    """Test 2: Beam battle and beam clash."""
    print("\n" + "="*60)
    print("TEST 2: BEAM BATTLE")
    print("="*60)
    
    # Get or create a test room
    room = ObjectDB.objects.filter(db_key__icontains="Combat Test").first()
    
    # Create two beam-capable NPCs
    npc1 = create_test_npc(room, "test_teknik", "BeamUser1")
    npc2 = create_test_npc(room, "test_teknik", "BeamUser2")
    
    print(f"\nBeam Users Created:")
    print(f"  {npc1.key}: PL={compute_current_pl(npc1)[0]}, Ki={npc1.db.ki_current}/{npc1.db.ki_max}")
    print(f"  {npc2.key}: PL={compute_current_pl(npc2)[0]}, Ki={npc2.db.ki_current}/{npc2.db.ki_max}")
    
    # Register beams targeting each other
    engage(npc1, npc2)
    
    # Fire beams at each other
    print(f"\n{npc1.key} fires a Kame Wave!")
    register_beam(npc1, npc2, "kame_wave", 50)
    
    print(f"{npc2.key} fires a Kame Wave!")
    register_beam(npc2, npc1, "kame_wave", 50)
    
    print("\n*** BEAM CLASH! ***")
    
    # Wait for beams to resolve
    time.sleep(3)
    
    print(f"\n--- Results ---")
    print(f"{npc1.key} HP: {npc1.db.hp_current}/{npc1.db.hp_max}")
    print(f"{npc2.key} HP: {npc2.db.hp_current}/{npc2.db.hp_max}")
    
    # Cleanup
    disengage(npc1)
    disengage(npc2)
    npc1.delete()
    npc2.delete()
    print("\nTest complete!")

def test_charging():
    """Test 3: Charging mechanics."""
    print("\n" + "="*60)
    print("TEST 3: CHARGING")
    print("="*60)
    
    room = ObjectDB.objects.filter(db_key__icontains="Combat Test").first()
    
    npc = create_test_npc(room, "test_charger", "Charger")
    
    pl_before, breakdown_before = compute_current_pl(npc)
    ki_before = npc.db.ki_current
    stacks_before = npc.db.charge_stacks or 0
    
    print(f"\nBefore charging:")
    print(f"  PL: {pl_before}")
    print(f"  Ki: {ki_before}/{npc.db.ki_max}")
    print(f"  Charge Stacks: {stacks_before}")
    print(f"  Charge Factor: {breakdown_before['charge_factor']}")
    
    # Start charging
    start_charging(npc, duration=10)
    print(f"\n{npc.key} starts charging!")
    
    # Let it charge for a few ticks
    print("\n--- Charging in progress ---")
    for i in range(5):
        time.sleep(1.1)
        pl_now, breakdown = compute_current_pl(npc)
        print(f"  Tick {i+1}: Ki={npc.db.ki_current}/{npc.db.ki_max}, Stacks={npc.db.charge_stacks}, PL={pl_now}")
    
    # Stop charging
    stop_charging(npc)
    
    pl_after, breakdown_after = compute_current_pl(npc)
    print(f"\n--- After charging ---")
    print(f"  PL: {pl_before} -> {pl_after} (+{pl_after - pl_before})")
    print(f"  Charge Factor: {breakdown_before['charge_factor']} -> {breakdown_after['charge_factor']}")
    
    # Cleanup
    npc.delete()
    print("\nTest complete!")

def test_transformation():
    """Test 4: Transformation mechanics."""
    print("\n" + "="*60)
    print("TEST 4: TRANSFORMATION")
    print("="*60)
    
    room = ObjectDB.objects.filter(db_key__icontains="Combat Test").first()
    
    npc = create_test_npc(room, "test_even", "Transformer")
    
    pl_before, breakdown_before = compute_current_pl(npc)
    ki_before = npc.db.ki_current
    
    print(f"\nBefore transformation:")
    print(f"  PL: {pl_before}")
    print(f"  Ki: {ki_before}/{npc.db.ki_max}")
    print(f"  Form Factor: {breakdown_before.get('form_factor', 1.0)}")
    
    # Activate Super Saiyan
    npc.db.active_form = "super_saiyan"
    
    pl_after, breakdown_after = compute_current_pl(npc)
    
    print(f"\n*** Super Saiyan transformation! ***")
    print(f"\nAfter transformation:")
    print(f"  PL: {pl_before} -> {pl_after} (+{pl_after - pl_before})")
    print(f"  Form Factor: {breakdown_after.get('form_factor', 1.0)}")
    print(f"  Speed Bias: {FORMS['super_saiyan']['speed_bias']}")
    print(f"  Ki Drain/tick: {FORMS['super_saiyan']['drain_per_tick']}")
    
    # Simulate a few ticks to show drain
    print("\n--- Transformation drain in progress (3 ticks) ---")
    for i in range(3):
        time.sleep(1)
        # Simulate the form drain
        ki_after = max(0, npc.db.ki_current - FORMS['super_saiyan']['drain_per_tick'])
        npc.db.ki_current = ki_after
        print(f"  Tick {i+1}: Ki={npc.db.ki_current}/{npc.db.ki_max}")
    
    # Deactivate
    npc.db.active_form = None
    pl_reverted, _ = compute_current_pl(npc)
    print(f"\n--- After reverting ---")
    print(f"  PL: {pl_after} -> {pl_reverted}")
    
    # Cleanup
    npc.delete()
    print("\nTest complete!")

def test_pl_gap():
    """Test 5: Power level gap mechanics."""
    print("\n" + "="*60)
    print("TEST 5: POWER LEVEL GAP")
    print("="*60)
    
    room = ObjectDB.objects.filter(db_key__icontains="Combat Test").first()
    
    # Create weak and strong NPCs
    npc_weak = create_test_npc(room, "test_weak", "WeakNPC")
    npc_strong = create_test_npc(room, "test_overwhelming", "StrongNPC")
    
    pl_weak, _ = compute_current_pl(npc_weak)
    pl_strong, _ = compute_current_pl(npc_strong)
    
    print(f"\nWeak NPC PL: {pl_weak}")
    print(f"Strong NPC PL: {pl_strong}")
    print(f"PL Ratio: {pl_strong/pl_weak:.1f}:1")
    
    # Calculate gap effects
    gap = pl_gap_effect(pl_strong, pl_weak)
    print(f"\nGap Effects (from strong to weak):")
    print(f"  Quality: {gap['quality']}")
    print(f"  Ratio: {gap['ratio']:.2f}")
    print(f"  Damage Mult: {gap['damage_mult']:.2f}")
    print(f"  Hit Bias: {gap['hit_bias']:.2f}")
    
    gap2 = pl_gap_effect(pl_weak, pl_strong)
    print(f"\nGap Effects (from weak to strong):")
    print(f"  Quality: {gap2['quality']}")
    print(f"  Ratio: {gap2['ratio']:.2f}")
    print(f"  Damage Mult: {gap2['damage_mult']:.2f}")
    print(f"  Hit Bias: {gap2['hit_bias']:.2f}")
    
    # Cleanup
    npc_weak.delete()
    npc_strong.delete()
    print("\nTest complete!")

def list_available_tests():
    """List all available test templates."""
    print("\n" + "="*60)
    print("AVAILABLE TEST NPC TEMPLATES")
    print("="*60)
    for name, template in TEST_NPC_TEMPLATES.items():
        print(f"\n{name}:")
        print(f"  Base Power: {template['base_power']}")
        print(f"  STR/SPD/BAL/MAS/KC: {template['strength']}/{template['speed']}/{template['balance']}/{template['mastery']}/{template['ki_control']}")
        print(f"  HP/Ki: {template['hp_max']}/{template['ki_max']}")
        print(f"  AI: {template['test_ai']}")

def main():
    print("="*60)
    print("DBFORGED COMBAT TEST SUITE")
    print("="*60)
    
    # List available templates
    list_available_tests()
    
    # Run tests
    test_basic_combat()
    test_beam_battle()
    test_charging()
    test_transformation()
    test_pl_gap()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
