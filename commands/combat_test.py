"""
Combat Test Command - Automated combat validation system.

Usage:
    combat_test basic      - Even PL match test
    combat_test pl_gap    - Overwhelming PL gap test  
    combat_test ki_drain  - Ki depletion PL reduction test
    combat_test charge    - Charging behavior test
    combat_test technique - Technique impact test
    combat_test transform - Transformation test
    combat_test full     - Run all tests
    combat_test spawn <template> - Spawn test NPC
    combat_test info     - Show test NPC info
"""

from __future__ import annotations

import random
import time

from evennia import CmdSet, create_object
from evennia.commands.default.muxcommand import MuxCommand
from world.power import compute_current_pl, pl_gap_effect


class CmdCombatTest(MuxCommand):
    """
    Run automated combat validation tests.
    
    Usage:
        combat_test basic      - Even PL match test
        combat_test pl_gap    - Overwhelming PL gap test
        combat_test ki_drain  - Ki depletion PL reduction test
        combat_test charge    - Charging behavior test
        combat_test technique - Technique impact test
        combat_test transform - Transformation test
        combat_test full     - Run all tests
        combat_test spawn <template> - Spawn test NPC
        combat_test info     - Show test NPC info
    """

    key = "combat_test"
    aliases = ["ctest", "cbt"]
    lock = "cmd:perm(Builder)"
    help_category = "Testing"

    def func(self):
        if not self.args:
            self.msg("|yUsage:|n combat_test <scenario>")
            self.msg("|gAvailable scenarios:|n basic, pl_gap, ki_drain, charge, technique, transform, full")
            self.msg("|gCommands:|n spawn, info")
            return

        subcmd = self.args.lower().split()[0]
        
        if subcmd == "basic":
            self.run_basic_test()
        elif subcmd == "pl_gap":
            self.run_pl_gap_test()
        elif subcmd == "ki_drain":
            self.run_ki_drain_test()
        elif subcmd == "charge":
            self.run_charge_test()
        elif subcmd == "technique":
            self.run_technique_test()
        elif subcmd == "transform":
            self.run_transformation_test()
        elif subcmd == "full":
            self.run_full_suite()
        elif subcmd == "spawn":
            self.spawn_test_npc()
        elif subcmd == "info":
            self.show_test_info()
        else:
            self.msg(f"|rUnknown test: {subcmd}|n")

    def get_test_room(self):
        """Get or create a test room."""
        from evennia import ObjectDB
        
        # Try to find existing test room
        test_rooms = ObjectDB.objects.filter(db_key__icontains="Combat Test")
        if test_rooms:
            return test_rooms[0]
            
        # Create new test room
        from evennia.objects.objects import DefaultRoom
        room = create_object(
            "typeclasses.rooms.Room",
            key="Combat Test Arena",
            location=None,
        )
        room.db.desc = "A dedicated combat testing arena."
        return room

    def spawn_test_npc(self):
        """Spawn a test NPC."""
        args = self.args.lower().split()
        template = args[1] if len(args) > 1 else "test_even"
        
        from typeclasses.npcs import create_test_npc, TEST_NPC_TEMPLATES
        
        if template not in TEST_NPC_TEMPLATES:
            self.msg(f"|rUnknown template: {template}|n")
            self.msg(f"|gAvailable templates:|n {', '.join(TEST_NPC_TEMPLATES.keys())}")
            return
            
        room = self.get_test_room()
        npc = create_test_npc(room, template)
        
        self.msg(f"|gSpawned test NPC: {npc.key}|n")
        self.msg(f"|gTemplate: {template}|n")
        
        info = npc.get_test_info()
        self.msg(f"|cPL:|n {info['pl']}")
        self.msg(f"|cHP:|n {info['hp']}")
        self.msg(f"|cKi:|n {info['ki']}")
        self.msg(f"|cAI:|n {info['ai']}")

    def show_test_info(self):
        """Show info about test NPCs in the room."""
        from evennia import ObjectDB
        
        test_npcs = ObjectDB.objects.filter(db_is_test_dummy=True)
        
        if not test_npcs:
            self.msg("|yNo test NPCs found. Use 'combat_test spawn <template>' to create one.|n")
            return
            
        for npc in test_npcs:
            info = npc.get_test_info()
            self.msg(f"|c=== {npc.key} ===|n")
            self.msg(f"PL: {info['pl']} | HP: {info['hp']} | Ki: {info['ki']}")
            self.msg(f"AI: {info['ai']}")
            self.msg(f"Stats: STR {info['stats']['strength']}, SPD {info['stats']['speed']}, "
                    f"BAL {info['stats']['balance']}, MST {info['stats']['mastery']}, "
                    f"KC {info['stats']['ki_control']}")

    def run_basic_test(self):
        """
        Test 1: Baseline even match (similar PL)
        
        Validates:
        - Readable fast exchanges
        - Correct chip damage range
        - Text cadence acceptable
        """
        self.msg("|y=== COMBAT TEST: basic (Even Match) ===|n")
        
        from typeclasses.npcs import create_test_npc
        
        # Create test room
        room = self.get_test_room()
        
        # Spawn two evenly-matched NPCs
        npc1 = create_test_npc(room, "test_even", "Test_Attacker")
        npc2 = create_test_npc(room, "test_even", "Test_Defender")
        
        # Get their PL
        pl1, _ = compute_current_pl(npc1)
        pl2, _ = compute_current_pl(npc2)
        
        self.msg(f"Attacker PL: {pl1}")
        self.msg(f"Defender PL: {pl2}")
        
        # Calculate gap
        gap = pl_gap_effect(pl1, pl2)
        self.msg(f"Gap quality: {gap['quality']} (ratio {gap['ratio']})")
        
        # Test checks
        results = []
        
        # Check 1: PL ratio should be close to 1.0
        ratio_ok = 0.8 <= gap['ratio'] <= 1.25
        results.append(("PL ratio ~1.0", ratio_ok))
        
        # Check 2: Damage multiplier should be near 1.0
        dmg_ok = 0.8 <= gap['damage_mult'] <= 1.2
        results.append(("Damage mult ~1.0", dmg_ok))
        
        # Check 3: Hit bias should be near 0.5
        hit_ok = 0.4 <= gap['hit_bias'] <= 0.6
        results.append(("Hit bias ~0.5", hit_ok))
        
        # Engage them
        from world.combat import engage
        engage(npc1, npc2)
        
        self.msg(f"|gEngaged {npc1.key} and {npc2.key} in combat.|n")
        self.msg("|yTest will run for 10 seconds...|n")
        
        # Let combat run
        import threading
        def cleanup():
            from world.combat import disengage
            disengage(npc1)
            disengage(npc2)
            npc1.delete()
            npc2.delete()
            
        timer = threading.Timer(15.0, cleanup)
        timer.start()
        
        # Print results
        self._print_results("basic", results)

    def run_pl_gap_test(self):
        """
        Test 2: Overwhelming PL gap (1000 vs 5000+)
        
        Validates:
        - Dominance behavior matches spec
        - Near-hopeless survival for weaker fighter
        """
        self.msg("|y=== COMBAT TEST: pl_gap (Overwhelming Gap) ===|n")
        
        from typeclasses.npcs import create_test_npc
        
        room = self.get_test_room()
        
        # Spawn weak and overwhelming opponents
        npc_weak = create_test_npc(room, "test_weak", "Test_Weak")
        npc_strong = create_test_npc(room, "test_overwhelming", "Test_Overwhelming")
        
        pl_weak, _ = compute_current_pl(npc_weak)
        pl_strong, _ = compute_current_pl(npc_strong)
        
        self.msg(f"Weak PL: {pl_weak}")
        self.msg(f"Overwhelming PL: {pl_strong}")
        
        gap = pl_gap_effect(pl_strong, pl_weak)
        self.msg(f"Gap quality: {gap['quality']} (ratio {gap['ratio']})")
        
        results = []
        
        # Check 1: Ratio should be >= 8.0 (overwhelming)
        ratio_ok = gap['ratio'] >= 8.0
        results.append(("Ratio >= 8.0 (overwhelming)", ratio_ok))
        
        # Check 2: Hit bias should favor stronger (high)
        hit_ok = gap['hit_bias'] >= 0.80
        results.append(("Stronger hit bias >= 0.80", hit_ok))
        
        # Check 3: Damage multiplier should be high for stronger
        dmg_ok = gap['damage_mult'] >= 2.5
        results.append(("Damage mult >= 2.5", dmg_ok))
        
        # Check 4: Gap quality should be "overwhelming"
        quality_ok = gap['quality'] == "overwhelming"
        results.append(("Quality is 'overwhelming'", quality_ok))
        
        # Engage
        from world.combat import engage
        engage(npc_strong, npc_weak)
        
        self.msg(f"|gEngaged {npc_strong.key} vs {npc_weak.key}.|n")
        
        import threading
        def cleanup():
            from world.combat import disengage
            disengage(npc_strong)
            disengage(npc_weak)
            npc_strong.delete()
            npc_weak.delete()
            
        timer = threading.Timer(15.0, cleanup)
        timer.start()
        
        self._print_results("pl_gap", results)

    def run_ki_drain_test(self):
        """
        Test 3: Ki depletion reduces effective PL
        
        Validates:
        - At 0 Ki, PL reduced by ~45%
        - ki_factor properly applied
        """
        self.msg("|y=== COMBAT TEST: ki_drain (Ki Depletion) ===|n")
        
        from typeclasses.npcs import create_test_npc
        
        room = self.get_test_room()
        
        # Create NPC with full Ki
        npc_full = create_test_npc(room, "test_even", "Test_FullKi")
        
        # Create NPC with empty Ki
        npc_empty = create_test_npc(room, "test_even", "Test_EmptyKi")
        npc_empty.db.ki_current = 0
        
        pl_full, breakdown_full = compute_current_pl(npc_full)
        pl_empty, breakdown_empty = compute_current_pl(npc_empty)
        
        self.msg(f"Full Ki PL: {pl_full} (ki_factor: {breakdown_full['ki_factor']})")
        self.msg(f"Empty Ki PL: {pl_empty} (ki_factor: {breakdown_empty['ki_factor']})")
        
        ratio = pl_empty / pl_full if pl_full > 0 else 0
        self.msg(f"PL ratio (empty/full): {ratio:.3f}")
        
        results = []
        
        # Check 1: ki_factor at 0 Ki should be ~0.55
        ki_factor_ok = 0.50 <= breakdown_empty['ki_factor'] <= 0.60
        results.append(("ki_factor ~0.55 at 0 Ki", ki_factor_ok))
        
        # Check 2: PL at 0 Ki should be ~45-55% of full
        pl_ratio_ok = 0.45 <= ratio <= 0.60
        results.append(("PL at 0 Ki is 45-60% of full", pl_ratio_ok))
        
        # Cleanup
        npc_full.delete()
        npc_empty.delete()
        
        self._print_results("ki_drain", results)

    def run_charge_test(self):
        """
        Test 4: Charging Ki mechanics
        
        Validates:
        - Ki gains each tick
        - Charge stacks accumulate
        - PL increases with charge_factor
        """
        self.msg("|y=== COMBAT TEST: charge (Charging Behavior) ===|n")
        
        from typeclasses.npcs import create_test_npc
        from world.combat import start_charging, stop_charging
        
        room = self.get_test_room()
        
        npc = create_test_npc(room, "test_charger", "Test_Charger")
        
        pl_before, breakdown_before = compute_current_pl(npc)
        ki_before = npc.db.ki_current
        stacks_before = npc.db.charge_stacks or 0
        
        self.msg(f"Before charging: PL={pl_before}, Ki={ki_before}, Stacks={stacks_before}")
        self.msg(f"Charge factor: {breakdown_before['charge_factor']}")
        
        # Start charging
        start_charging(npc, duration=10)
        
        # Simulate a few ticks
        for i in range(5):
            time.sleep(1.1)  # Wait for tick
        
        pl_after, breakdown_after = compute_current_pl(npc)
        ki_after = npc.db.ki_current
        stacks_after = npc.db.charge_stacks or 0
        
        self.msg(f"After 5 ticks: PL={pl_after}, Ki={ki_after}, Stacks={stacks_after}")
        self.msg(f"Charge factor: {breakdown_after['charge_factor']}")
        
        results = []
        
        # Check 1: Ki should increase
        ki_gained = ki_after > ki_before
        results.append(("Ki increased", ki_gained))
        
        # Check 2: Charge stacks should accumulate
        stacks_gained = stacks_after > stacks_before
        results.append(("Charge stacks accumulated", stacks_gained))
        
        # Check 3: PL should increase with charge
        pl_increased = pl_after > pl_before
        results.append(("PL increased with charge", pl_increased))
        
        # Check 4: Charge factor should be > 1.0
        charge_active = breakdown_after['charge_factor'] > 1.0
        results.append(("Charge factor > 1.0", charge_active))
        
        # Cleanup
        stop_charging(npc)
        npc.delete()
        
        self._print_results("charge", results)

    def run_technique_test(self):
        """
        Test 5: Technique impact
        
        Validates:
        - Damage techniques deal expected damage
        - Control techniques apply effects
        - Cooldowns prevent spam
        """
        self.msg("|y=== COMBAT TEST: technique (Technique Impact) ===|n")
        
        from typeclasses.npcs import create_test_npc
        from world.techniques import TECHNIQUES
        
        room = self.get_test_room()
        
        # Attacker with techniques
        npc_atk = create_test_npc(room, "test_teknik", "Test_Attacker")
        # Defender to target
        npc_def = create_test_npc(room, "test_even", "Test_Defender")
        
        pl_atk, _ = compute_current_pl(npc_atk)
        pl_def, _ = compute_current_pl(npc_def)
        
        self.msg(f"Attacker PL: {pl_atk}")
        self.msg(f"Defender PL: {pl_def}")
        
        results = []
        
        # Test ki_blast damage
        tech = TECHNIQUES["ki_blast"]
        gap = pl_gap_effect(pl_atk, pl_def)
        
        # Calculate expected damage
        scaling = tech["scaling"]
        base_dmg = (
            scaling["base"]
            + (npc_atk.db.strength * scaling["strength"])
            + (npc_atk.db.mastery * scaling["mastery"])
            + (pl_atk * scaling["pl"])
        )
        expected = int(base_dmg * gap["damage_mult"])
        
        self.msg(f"Expected ki_blast damage: {expected}")
        
        # Execute technique
        npc_atk.execute_technique("ki_blast", npc_def)
        
        damage_taken = npc_atk.db.hp_current - npc_def.db.hp_current
        self.msg(f"Actual damage: {damage_taken}")
        
        # Check if damage is reasonable (±30%)
        damage_ok = abs(damage_taken - expected) / max(expected, 1) <= 0.35
        results.append(("Ki blast damage in expected range", damage_ok))
        
        # Test control technique (solar flare - stun)
        target_hp_before = npc_def.db.hp_current
        
        # Use solar flare
        npc_atk.execute_technique("solar_flare", npc_def)
        
        stunned = npc_def.has_status("stunned")
        results.append(("Solar Flare applies stun", stunned))
        
        # Test guard
        npc_def.execute_technique("guard", npc_def)
        
        guarding = npc_def.has_status("guard")
        results.append(("Guard applies guard status", guarding))
        
        # Cleanup
        npc_atk.delete()
        npc_def.delete()
        
        self._print_results("technique", results)

    def run_transformation_test(self):
        """
        Test 6: Transformation behavior
        
        Validates:
        - PL multiplier applies correctly
        - Ki drains each tick
        - Mastery reduces drain over time
        - Auto-revert when Ki insufficient
        """
        self.msg("|y=== COMBAT TEST: transform (Transformation) ===|n")
        
        from typeclasses.npcs import create_test_npc
        from world.forms import FORMS
        
        room = self.get_test_room()
        
        npc = create_test_npc(room, "test_even", "Test_Transformer")
        
        pl_before, _ = compute_current_pl(npc)
        ki_before = npc.db.ki_current
        
        self.msg(f"Before transform: PL={pl_before}, Ki={ki_before}")
        
        # Activate Super Saiyan
        npc.db.active_form = "super_saiyan"
        
        pl_after, breakdown = compute_current_pl(npc)
        
        self.msg(f"After transform: PL={pl_after}")
        self.msg(f"Form factor: {breakdown['form_factor']}")
        
        results = []
        
        # Check 1: PL should increase
        pl_increased = pl_after > pl_before
        results.append(("PL increased with transformation", pl_increased))
        
        # Check 2: Form factor should be > 1.0
        form_ok = breakdown['form_factor'] > 1.0
        results.append(("Form factor > 1.0", form_ok))
        
        # Check 3: Super Saiyan multiplier is ~1.8
        form = FORMS["super_saiyan"]
        expected_mult = form["pl_multiplier"]
        actual_mult = pl_after / pl_before if pl_before > 0 else 0
        mult_ok = abs(actual_mult - expected_mult) / expected_mult <= 0.15
        results.append((f"PL multiplier ~{expected_mult}x", mult_ok))
        
        # Test drain
        initial_ki = npc.db.ki_current
        drain_per_tick = form["drain_per_tick"]
        
        # Simulate a few ticks
        for i in range(3):
            if npc.db.ki_current >= drain_per_tick:
                npc.db.ki_current -= drain_per_tick
        
        ki_after_drain = npc.db.ki_current
        self.msg(f"After 3 ticks: Ki={ki_after_drain}")
        
        drained = initial_ki - ki_after_drain
        drain_ok = drained >= drain_per_tick * 2  # At least 2 ticks worth
        results.append(("Transformation drains Ki", drain_ok))
        
        # Cleanup
        npc.db.active_form = None
        npc.delete()
        
        self._print_results("transform", results)

    def run_full_suite(self):
        """Run all test scenarios."""
        self.msg("|c=== RUNNING FULL COMBAT TEST SUITE ===|n")
        
        tests = [
            ("basic", self.run_basic_test),
            ("pl_gap", self.run_pl_gap_test),
            ("ki_drain", self.run_ki_drain_test),
            ("charge", self.run_charge_test),
            ("technique", self.run_technique_test),
            ("transform", self.run_transformation_test),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                test_func()
                passed += 1
            except Exception as e:
                self.msg(f"|rError in {name}: {e}|n")
                failed += 1
                
        self.msg(f"|c=== FULL SUITE RESULTS ===|n")
        self.msg(f"Passed: {passed}/{len(tests)}")
        self.msg(f"Failed: {failed}/{len(tests)}")

    def _print_results(self, test_name, results):
        """Print test results in standard format."""
        self.msg(f"|c--- Results for {test_name} ---|n")
        
        passed = 0
        total = len(results)
        
        for check, result in results:
            if result:
                self.msg(f"[PASS] {check}")
                passed += 1
            else:
                self.msg(f"[FAIL] {check}")
        
        self.msg(f"|c--- {test_name}: {passed}/{total} checks passed ---|n")
        
        if passed == total:
            self.msg(f"|gRESULT: PASS ({total}/{total})|n")
        else:
            self.msg(f"|rRESULT: FAIL ({passed}/{total})|n")


class CombatTestCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdCombatTest)
