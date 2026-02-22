"""
DBForged combat damage simulator (CLI).

Uses the live DB vertical-slice technique and PL formulas so balance checks
track the game's current implementation.

Examples:
    python live/tools/combat_simulator.py list-techs
    python live/tools/combat_simulator.py snapshot --tech kame_wave --attacker-level 10 --defender-level 10
    python live/tools/combat_simulator.py sweep --tech ki_blast --levels 1:20 --vs-level 10
    python live/tools/combat_simulator.py duel --duration 30 --iterations 500 --seed 7
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
LIVE_DIR = ROOT / "live"
if str(LIVE_DIR) not in sys.path:
    sys.path.insert(0, str(LIVE_DIR))

from world.power import compute_current_pl, pl_gap_effect  # noqa: E402
from world.techniques import TECHNIQUES, is_beam  # noqa: E402


RACES = ("saiyan", "human", "namekian", "frost_demon", "android", "majin")


LEVEL_PROFILES = {
    # Gains are per level after level 1. Keep conservative to match current vertical slice.
    "balanced": {
        "base_power": 120,
        "hp_max": 120,
        "ki_max": 90,
        "strength": 10,
        "speed": 10,
        "balance": 10,
        "mastery": 10,
        "ki_control": 5,
        "gain": {
            "base_power": 11,
            "hp_max": 8,
            "ki_max": 6,
            "strength": 0.55,
            "speed": 0.50,
            "balance": 0.48,
            "mastery": 0.55,
            "ki_control": 0.45,
        },
    },
    "striker": {
        "base_power": 124,
        "hp_max": 118,
        "ki_max": 86,
        "strength": 11,
        "speed": 10,
        "balance": 9,
        "mastery": 10,
        "ki_control": 4,
        "gain": {
            "base_power": 12,
            "hp_max": 7,
            "ki_max": 5,
            "strength": 0.78,
            "speed": 0.60,
            "balance": 0.35,
            "mastery": 0.52,
            "ki_control": 0.30,
        },
    },
    "controller": {
        "base_power": 116,
        "hp_max": 116,
        "ki_max": 96,
        "strength": 9,
        "speed": 10,
        "balance": 11,
        "mastery": 11,
        "ki_control": 7,
        "gain": {
            "base_power": 10,
            "hp_max": 7,
            "ki_max": 8,
            "strength": 0.38,
            "speed": 0.45,
            "balance": 0.60,
            "mastery": 0.72,
            "ki_control": 0.65,
        },
    },
    "bruiser": {
        "base_power": 122,
        "hp_max": 130,
        "ki_max": 82,
        "strength": 11,
        "speed": 8,
        "balance": 10,
        "mastery": 9,
        "ki_control": 4,
        "gain": {
            "base_power": 11,
            "hp_max": 10,
            "ki_max": 4,
            "strength": 0.72,
            "speed": 0.28,
            "balance": 0.52,
            "mastery": 0.35,
            "ki_control": 0.25,
        },
    },
}


RACE_MODIFIERS = {
    "saiyan": {"base_power": 1.06, "strength": 1.06, "speed": 1.03, "ki_control": 0.96},
    "human": {"base_power": 1.00, "balance": 1.05, "mastery": 1.04, "ki_control": 1.05},
    "namekian": {"hp_max": 1.10, "balance": 1.07, "ki_control": 1.08, "strength": 0.98},
    "frost_demon": {"base_power": 1.05, "speed": 1.06, "mastery": 1.04, "ki_control": 1.00},
    "android": {"ki_max": 1.15, "ki_control": 1.10, "balance": 1.03, "base_power": 0.98},
    "majin": {"hp_max": 1.12, "strength": 1.04, "speed": 0.95, "balance": 1.02},
}


def clamp(value, low, high):
    return max(low, min(high, value))


def round_stat(v):
    return int(round(v))


class DummyCharacter:
    """
    Minimal adapter for world.power.compute_current_pl.
    """

    def __init__(self, attrs):
        self.db = SimpleNamespace(**attrs)

    def has_status(self, name):
        statuses = getattr(self.db, "statuses", {}) or {}
        return name in statuses

    def get_status_data(self, name):
        statuses = getattr(self.db, "statuses", {}) or {}
        return statuses.get(name, {})

    def get_current_pl(self):
        return compute_current_pl(self)


@dataclass
class FighterState:
    name: str
    race: str = "human"
    profile: str = "balanced"
    level: int = 1
    hp_ratio: float = 1.0
    ki_ratio: float = 1.0
    charge_stacks: int = 0
    suppressed: bool = False
    active_form: str | None = None
    form_mastery: int = 0
    guard_until: float = 0.0
    afterimage_until: float = 0.0
    stunned_until: float = 0.0
    tech_mastery: dict = field(default_factory=dict)
    cooldowns: dict = field(default_factory=dict)
    hp_current: int = 0
    ki_current: int = 0
    hp_max: int = 0
    ki_max: int = 0
    attrs: dict = field(default_factory=dict)

    @classmethod
    def from_level(
        cls,
        *,
        name: str,
        level: int,
        race: str,
        profile: str,
        hp_ratio: float = 1.0,
        ki_ratio: float = 1.0,
        charge_stacks: int = 0,
        suppressed: bool = False,
        active_form: str | None = None,
        form_mastery: int = 0,
    ):
        attrs = build_level_attrs(level=level, race=race, profile=profile)
        hp_max = attrs["hp_max"]
        ki_max = attrs["ki_max"]
        hp_current = max(1, int(hp_max * clamp(hp_ratio, 0.01, 1.0)))
        ki_current = max(0, int(ki_max * clamp(ki_ratio, 0.0, 1.0)))
        inst = cls(
            name=name,
            race=race,
            profile=profile,
            level=level,
            hp_ratio=hp_ratio,
            ki_ratio=ki_ratio,
            charge_stacks=charge_stacks,
            suppressed=suppressed,
            active_form=active_form,
            form_mastery=form_mastery,
            hp_current=hp_current,
            ki_current=ki_current,
            hp_max=hp_max,
            ki_max=ki_max,
            attrs=attrs,
        )
        inst.sync_attrs()
        return inst

    def clone(self, new_name=None):
        cloned = FighterState(
            name=new_name or self.name,
            race=self.race,
            profile=self.profile,
            level=self.level,
            hp_ratio=self.hp_ratio,
            ki_ratio=self.ki_ratio,
            charge_stacks=self.charge_stacks,
            suppressed=self.suppressed,
            active_form=self.active_form,
            form_mastery=self.form_mastery,
            guard_until=self.guard_until,
            afterimage_until=self.afterimage_until,
            stunned_until=self.stunned_until,
            tech_mastery=dict(self.tech_mastery),
            cooldowns=dict(self.cooldowns),
            hp_current=self.hp_current,
            ki_current=self.ki_current,
            hp_max=self.hp_max,
            ki_max=self.ki_max,
            attrs=dict(self.attrs),
        )
        cloned.sync_attrs()
        return cloned

    def sync_attrs(self):
        attrs = dict(self.attrs)
        attrs.update(
            {
                "race": self.race,
                "hp_current": self.hp_current,
                "hp_max": self.hp_max,
                "ki_current": self.ki_current,
                "ki_max": self.ki_max,
                "charge_stacks": self.charge_stacks,
                "suppressed": self.suppressed,
                "suppression_factor": 0.35,
                "active_form": self.active_form,
                "form_mastery": {self.active_form: self.form_mastery} if self.active_form else {},
                "statuses": {},
            }
        )
        if self.has_guard(0):
            attrs["statuses"]["guard"] = {"reduction": TECHNIQUES["guard"]["effect"]["reduction"]}
        if self.is_afterimage(0):
            attrs["statuses"]["afterimage"] = {}
        self._dummy = DummyCharacter(attrs)
        return self

    def has_guard(self, now):
        return self.guard_until > now

    def is_afterimage(self, now):
        return self.afterimage_until > now

    def is_stunned(self, now):
        return self.stunned_until > now

    def current_pl(self):
        self.sync_attrs()
        return self._dummy.get_current_pl()

    def spend_ki(self, amount):
        if self.ki_current < amount:
            return False
        self.ki_current -= amount
        return True

    def restore_ki(self, amount):
        self.ki_current = min(self.ki_max, self.ki_current + amount)

    def take_damage(self, amount, now):
        dmg = max(0, int(amount))
        if self.has_guard(now):
            reduction = TECHNIQUES["guard"]["effect"]["reduction"]
            dmg = int(round(dmg * (1.0 - reduction)))
        self.hp_current = max(0, self.hp_current - dmg)
        return dmg


def build_level_attrs(*, level: int, race: str, profile: str) -> dict:
    if profile not in LEVEL_PROFILES:
        raise ValueError(f"Unknown profile '{profile}'.")
    if race not in RACES:
        raise ValueError(f"Unknown race '{race}'.")
    level = max(1, int(level))
    p = LEVEL_PROFILES[profile]
    gains = p["gain"]
    mult = RACE_MODIFIERS.get(race, {})
    n = level - 1

    attrs = {}
    for key in ("base_power", "hp_max", "ki_max", "strength", "speed", "balance", "mastery", "ki_control"):
        raw = p[key] + gains[key] * n
        raw *= mult.get(key, 1.0)
        if key in {"strength", "speed", "balance", "mastery", "ki_control"}:
            attrs[key] = max(1, round_stat(raw))
        else:
            attrs[key] = max(1, int(round(raw)))
    return attrs


def tech_mastery_for_level(level: int, mode: str = "linear") -> int:
    level = max(1, int(level))
    if mode == "zero":
        return 0
    if mode == "linear":
        return int((level - 1) * 2.0)
    if mode == "focused":
        return int((level - 1) * 3.2)
    if mode == "veteran":
        return int((level - 1) * 2.5 + 15)
    raise ValueError(f"Unknown mastery mode '{mode}'")


def compute_tech_damage(attacker: FighterState, defender: FighterState, tech_key: str, tech_mastery_level: int = 0, now: float = 0.0):
    tech = TECHNIQUES[tech_key]
    if "scaling" not in tech:
        return {
            "tech_key": tech_key,
            "tech_name": tech["name"],
            "category": tech["category"],
            "has_damage": False,
            "effect": tech.get("effect"),
        }

    a_pl, a_break = attacker.current_pl()
    d_pl, d_break = defender.current_pl()
    gap = pl_gap_effect(a_pl, d_pl)
    scaling = tech["scaling"]
    base_damage = (
        scaling["base"]
        + int((attacker.attrs["strength"] or 10) * scaling["strength"])
        + int((attacker.attrs["mastery"] or 10) * scaling["mastery"])
        + int(a_pl * scaling["pl"])
        + int(tech_mastery_level * 0.7)
    )
    raw_damage = int(base_damage * gap["damage_mult"])
    final_damage = raw_damage
    if defender.has_guard(now):
        final_damage = int(round(final_damage * (1.0 - TECHNIQUES["guard"]["effect"]["reduction"])))

    expected_damage = final_damage * gap["hit_bias"]
    return {
        "tech_key": tech_key,
        "tech_name": tech["name"],
        "category": tech["category"],
        "beam": bool(is_beam(tech_key)),
        "has_damage": True,
        "ki_cost": tech["ki_cost"],
        "cooldown": tech["cooldown"],
        "cast_time": tech["cast_time"],
        "attacker_pl": a_pl,
        "defender_pl": d_pl,
        "attacker_breakdown": a_break,
        "defender_breakdown": d_break,
        "gap": gap,
        "base_damage": base_damage,
        "raw_damage": raw_damage,
        "final_damage": final_damage,
        "expected_damage": round(expected_damage, 2),
        "dph": round(expected_damage / max(1, tech["ki_cost"]), 2),
    }


def list_techs():
    rows = []
    for key, tech in TECHNIQUES.items():
        row = {
            "key": key,
            "name": tech["name"],
            "category": tech["category"],
            "ki_cost": tech["ki_cost"],
            "cooldown": tech["cooldown"],
            "cast_time": tech["cast_time"],
            "damage": "scaling" in tech,
            "tags": ",".join(tech.get("tags", [])),
        }
        rows.append(row)
    return rows


def parse_level_range(text: str):
    if ":" in text:
        start, end = text.split(":", 1)
        return list(range(int(start), int(end) + 1))
    if "," in text:
        return [int(x.strip()) for x in text.split(",") if x.strip()]
    return [int(text)]


def print_table(headers, rows):
    widths = [len(h) for h in headers]
    rows_str = []
    for row in rows:
        vals = [str(row.get(h, "")) for h in headers]
        rows_str.append(vals)
        widths = [max(widths[i], len(vals[i])) for i in range(len(headers))]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for vals in rows_str:
        print(fmt.format(*vals))


def cmd_list(args):
    rows = list_techs()
    print_table(
        ["key", "name", "category", "ki_cost", "cooldown", "cast_time", "damage", "tags"],
        rows,
    )


def build_pair_from_args(args):
    a = FighterState.from_level(
        name="Attacker",
        level=args.attacker_level,
        race=args.attacker_race,
        profile=args.attacker_profile,
        hp_ratio=args.attacker_hp_ratio,
        ki_ratio=args.attacker_ki_ratio,
        charge_stacks=args.attacker_charge,
        suppressed=args.attacker_suppressed,
        active_form=args.attacker_form,
        form_mastery=args.attacker_form_mastery,
    )
    d = FighterState.from_level(
        name="Defender",
        level=args.defender_level,
        race=args.defender_race,
        profile=args.defender_profile,
        hp_ratio=args.defender_hp_ratio,
        ki_ratio=args.defender_ki_ratio,
        charge_stacks=args.defender_charge,
        suppressed=args.defender_suppressed,
        active_form=args.defender_form,
        form_mastery=args.defender_form_mastery,
    )
    if args.defender_guarded:
        d.guard_until = 999999
    return a, d


def cmd_snapshot(args):
    if args.tech not in TECHNIQUES:
        raise SystemExit(f"Unknown technique: {args.tech}")
    attacker, defender = build_pair_from_args(args)
    mastery_level = args.tech_mastery if args.tech_mastery is not None else tech_mastery_for_level(attacker.level, args.tech_mastery_mode)
    result = compute_tech_damage(attacker, defender, args.tech, tech_mastery_level=mastery_level)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"{result['tech_name']} ({args.tech})")
    print(f"Attacker L{attacker.level} {attacker.race}/{attacker.profile} vs Defender L{defender.level} {defender.race}/{defender.profile}")
    print(f"Tech mastery level: {mastery_level}")
    print(f"Attacker PL: {result.get('attacker_pl')}  Defender PL: {result.get('defender_pl')}")
    print(f"Gap: {result['gap']['quality']} (ratio {result['gap']['ratio']}, dmg x{result['gap']['damage_mult']}, hit {result['gap']['hit_bias']})")
    if result["has_damage"]:
        print(f"Base damage: {result['base_damage']}")
        print(f"Raw damage (after PL gap): {result['raw_damage']}")
        print(f"Final damage (after guard/situation): {result['final_damage']}")
        print(f"Expected damage (hit-weighted): {result['expected_damage']}")
        print(f"Damage per Ki (expected): {result['dph']}")
    else:
        print("This technique has no damage scaling (control/defense/movement utility).")


def cmd_sweep(args):
    if args.tech not in TECHNIQUES:
        raise SystemExit(f"Unknown technique: {args.tech}")
    levels = parse_level_range(args.levels)
    rows = []
    for lvl in levels:
        attacker = FighterState.from_level(
            name="Attacker",
            level=lvl,
            race=args.attacker_race,
            profile=args.attacker_profile,
            hp_ratio=args.attacker_hp_ratio,
            ki_ratio=args.attacker_ki_ratio,
            charge_stacks=args.attacker_charge,
            suppressed=args.attacker_suppressed,
            active_form=args.attacker_form,
            form_mastery=args.attacker_form_mastery,
        )
        defender = FighterState.from_level(
            name="Defender",
            level=args.vs_level if args.vs_level else lvl,
            race=args.defender_race,
            profile=args.defender_profile,
            hp_ratio=args.defender_hp_ratio,
            ki_ratio=args.defender_ki_ratio,
            charge_stacks=args.defender_charge,
            suppressed=args.defender_suppressed,
            active_form=args.defender_form,
            form_mastery=args.defender_form_mastery,
        )
        if args.defender_guarded:
            defender.guard_until = 999999
        mastery_level = args.tech_mastery if args.tech_mastery is not None else tech_mastery_for_level(lvl, args.tech_mastery_mode)
        r = compute_tech_damage(attacker, defender, args.tech, tech_mastery_level=mastery_level)
        rows.append(
            {
                "level": lvl,
                "tech_m": mastery_level,
                "atk_pl": r.get("attacker_pl", "-"),
                "def_pl": r.get("defender_pl", "-"),
                "gap": r["gap"]["quality"] if r.get("gap") else "-",
                "ratio": r["gap"]["ratio"] if r.get("gap") else "-",
                "base": r.get("base_damage", "-"),
                "raw": r.get("raw_damage", "-"),
                "final": r.get("final_damage", "-"),
                "exp": r.get("expected_damage", "-"),
                "dpk": r.get("dph", "-"),
            }
        )
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    print_table(["level", "tech_m", "atk_pl", "def_pl", "gap", "ratio", "base", "raw", "final", "exp", "dpk"], rows)


def choose_next_tech(rotation, fighter: FighterState, now: float):
    for tech_key in rotation:
        tech = TECHNIQUES[tech_key]
        if fighter.cooldowns.get(tech_key, 0.0) > now:
            continue
        if fighter.ki_current < tech["ki_cost"]:
            continue
        return tech_key
    return None


def apply_non_damage_tech(user: FighterState, target: FighterState, tech_key: str, now: float):
    tech = TECHNIQUES[tech_key]
    effect = tech.get("effect", {})
    if tech_key == "guard":
        user.guard_until = max(user.guard_until, now + effect.get("duration", 0))
    elif tech_key == "afterimage_dash":
        user.afterimage_until = max(user.afterimage_until, now + effect.get("duration", 0))
    elif tech_key == "solar_flare":
        target.stunned_until = max(target.stunned_until, now + effect.get("duration", 0))


def simulate_duel(
    attacker_template: FighterState,
    defender_template: FighterState,
    *,
    attacker_rotation,
    defender_rotation,
    duration: float,
    iterations: int,
    seed: int | None = None,
    tech_mastery_mode: str = "linear",
    ki_regen_per_sec: float = 0.0,
):
    rng = random.Random(seed)
    results = []

    for i in range(iterations):
        a = attacker_template.clone("Attacker")
        b = defender_template.clone("Defender")
        # Seed mastery based on level
        for tech_key in TECHNIQUES:
            a.tech_mastery[tech_key] = tech_mastery_for_level(a.level, tech_mastery_mode)
            b.tech_mastery[tech_key] = tech_mastery_for_level(b.level, tech_mastery_mode)

        now = 0.0
        step = 0.25
        a_damage_done = 0
        b_damage_done = 0
        a_casts = 0
        b_casts = 0
        log = []

        while now < duration and a.hp_current > 0 and b.hp_current > 0:
            for actor, target, rotation, tag in ((a, b, attacker_rotation, "A"), (b, a, defender_rotation, "B")):
                if actor.hp_current <= 0 or target.hp_current <= 0:
                    continue
                if actor.is_stunned(now):
                    continue
                tech_key = choose_next_tech(rotation, actor, now)
                if not tech_key:
                    continue
                tech = TECHNIQUES[tech_key]
                if not actor.spend_ki(tech["ki_cost"]):
                    continue
                mastery_level = actor.tech_mastery.get(tech_key, 0)
                actor.cooldowns[tech_key] = now + tech["cooldown"]
                if "scaling" not in tech:
                    apply_non_damage_tech(actor, target, tech_key, now)
                    log.append((round(now, 2), tag, tech_key, "utility", 0))
                    continue
                result = compute_tech_damage(actor, target, tech_key, mastery_level, now=now)
                hit_bias = result["gap"]["hit_bias"]
                # afterimage gives extra evasion in simulator (approximation)
                if target.is_afterimage(now):
                    hit_bias = clamp(hit_bias - 0.18, 0.02, 0.95)
                hit = rng.random() < hit_bias
                dealt = target.take_damage(result["raw_damage"], now=now) if hit else 0
                if actor is a:
                    a_damage_done += dealt
                    a_casts += 1
                else:
                    b_damage_done += dealt
                    b_casts += 1
                log.append((round(now, 2), tag, tech_key, "hit" if hit else "miss", dealt))
            if ki_regen_per_sec > 0:
                regen = max(0, int(ki_regen_per_sec * step))
                if regen:
                    a.restore_ki(regen)
                    b.restore_ki(regen)
            now += step

        winner = "attacker" if a.hp_current > b.hp_current else "defender" if b.hp_current > a.hp_current else "draw"
        if a.hp_current <= 0 and b.hp_current > 0:
            winner = "defender"
        elif b.hp_current <= 0 and a.hp_current > 0:
            winner = "attacker"
        elif a.hp_current <= 0 and b.hp_current <= 0:
            winner = "draw"
        results.append(
            {
                "winner": winner,
                "attacker_damage": a_damage_done,
                "defender_damage": b_damage_done,
                "attacker_hp_left": a.hp_current,
                "defender_hp_left": b.hp_current,
                "attacker_casts": a_casts,
                "defender_casts": b_casts,
                "timeline": log,
            }
        )
    return results


def summarize_duel(results):
    wins_a = sum(1 for r in results if r["winner"] == "attacker")
    wins_b = sum(1 for r in results if r["winner"] == "defender")
    draws = len(results) - wins_a - wins_b
    a_dmg = [r["attacker_damage"] for r in results]
    b_dmg = [r["defender_damage"] for r in results]
    return {
        "iterations": len(results),
        "attacker_win_rate": round(wins_a / max(1, len(results)), 3),
        "defender_win_rate": round(wins_b / max(1, len(results)), 3),
        "draw_rate": round(draws / max(1, len(results)), 3),
        "attacker_damage_avg": round(statistics.fmean(a_dmg), 2) if a_dmg else 0,
        "defender_damage_avg": round(statistics.fmean(b_dmg), 2) if b_dmg else 0,
        "attacker_damage_p90": percentile(a_dmg, 90),
        "defender_damage_p90": percentile(b_dmg, 90),
        "attacker_hp_left_avg": round(statistics.fmean([r["attacker_hp_left"] for r in results]), 2),
        "defender_hp_left_avg": round(statistics.fmean([r["defender_hp_left"] for r in results]), 2),
    }


def percentile(values, p):
    if not values:
        return 0
    ordered = sorted(values)
    idx = int(math.ceil((p / 100) * len(ordered))) - 1
    idx = clamp(idx, 0, len(ordered) - 1)
    return ordered[idx]


def cmd_duel(args):
    a = FighterState.from_level(
        name="Attacker",
        level=args.attacker_level,
        race=args.attacker_race,
        profile=args.attacker_profile,
        hp_ratio=args.attacker_hp_ratio,
        ki_ratio=args.attacker_ki_ratio,
        charge_stacks=args.attacker_charge,
        suppressed=args.attacker_suppressed,
        active_form=args.attacker_form,
        form_mastery=args.attacker_form_mastery,
    )
    b = FighterState.from_level(
        name="Defender",
        level=args.defender_level,
        race=args.defender_race,
        profile=args.defender_profile,
        hp_ratio=args.defender_hp_ratio,
        ki_ratio=args.defender_ki_ratio,
        charge_stacks=args.defender_charge,
        suppressed=args.defender_suppressed,
        active_form=args.defender_form,
        form_mastery=args.defender_form_mastery,
    )

    attacker_rotation = [t.strip() for t in args.attacker_rotation.split(",") if t.strip()]
    defender_rotation = [t.strip() for t in args.defender_rotation.split(",") if t.strip()]
    for t in attacker_rotation + defender_rotation:
        if t not in TECHNIQUES:
            raise SystemExit(f"Unknown technique in rotation: {t}")

    results = simulate_duel(
        a,
        b,
        attacker_rotation=attacker_rotation,
        defender_rotation=defender_rotation,
        duration=args.duration,
        iterations=args.iterations,
        seed=args.seed,
        tech_mastery_mode=args.tech_mastery_mode,
        ki_regen_per_sec=args.ki_regen_per_sec,
    )
    summary = summarize_duel(results)

    if args.json:
        payload = {"summary": summary}
        if args.include_samples:
            payload["samples"] = results[: args.include_samples]
        print(json.dumps(payload, indent=2))
        return

    print("Duel Simulation Summary")
    print(
        f"Attacker L{a.level} {a.race}/{a.profile} ({attacker_rotation}) vs "
        f"Defender L{b.level} {b.race}/{b.profile} ({defender_rotation})"
    )
    for k, v in summary.items():
        print(f"- {k}: {v}")
    if args.include_samples:
        print("\nSample timelines:")
        for idx, r in enumerate(results[: args.include_samples], 1):
            print(f"\nRun {idx}: winner={r['winner']} A_dmg={r['attacker_damage']} B_dmg={r['defender_damage']}")
            for t, side, tech, outcome, dmg in r["timeline"][:30]:
                print(f"  t={t:>5} {side} {tech:<15} {outcome:<6} dmg={dmg}")


def add_common_fighter_args(parser: argparse.ArgumentParser, prefix: str):
    parser.add_argument(f"--{prefix}-level", type=int, default=10)
    parser.add_argument(f"--{prefix}-race", choices=RACES, default="human")
    parser.add_argument(f"--{prefix}-profile", choices=sorted(LEVEL_PROFILES), default="balanced")
    parser.add_argument(f"--{prefix}-hp-ratio", type=float, default=1.0)
    parser.add_argument(f"--{prefix}-ki-ratio", type=float, default=1.0)
    parser.add_argument(f"--{prefix}-charge", type=int, default=0)
    parser.add_argument(f"--{prefix}-suppressed", action="store_true")
    parser.add_argument(f"--{prefix}-form", default=None, help="Form key from world.forms.FORMS")
    parser.add_argument(f"--{prefix}-form-mastery", type=int, default=0)


def build_parser():
    parser = argparse.ArgumentParser(description="DBForged combat simulator using live formulas.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list-techs", help="List currently defined techniques.")
    p_list.set_defaults(func=cmd_list)

    p_snap = sub.add_parser("snapshot", help="Compute one technique damage snapshot for a matchup.")
    p_snap.add_argument("--tech", required=True, choices=sorted(TECHNIQUES))
    add_common_fighter_args(p_snap, "attacker")
    add_common_fighter_args(p_snap, "defender")
    p_snap.add_argument("--defender-guarded", action="store_true")
    p_snap.add_argument("--tech-mastery", type=int, default=None)
    p_snap.add_argument("--tech-mastery-mode", choices=("zero", "linear", "focused", "veteran"), default="linear")
    p_snap.add_argument("--json", action="store_true")
    p_snap.set_defaults(func=cmd_snapshot)

    p_sweep = sub.add_parser("sweep", help="Run a level sweep for one technique.")
    p_sweep.add_argument("--tech", required=True, choices=sorted(TECHNIQUES))
    p_sweep.add_argument("--levels", default="1:20", help="Range '1:20', csv '1,5,10', or single level.")
    p_sweep.add_argument("--vs-level", type=int, default=0, help="Fixed defender level (default: same as attacker).")
    add_common_fighter_args(p_sweep, "attacker")
    add_common_fighter_args(p_sweep, "defender")
    p_sweep.add_argument("--defender-guarded", action="store_true")
    p_sweep.add_argument("--tech-mastery", type=int, default=None)
    p_sweep.add_argument("--tech-mastery-mode", choices=("zero", "linear", "focused", "veteran"), default="linear")
    p_sweep.add_argument("--json", action="store_true")
    p_sweep.set_defaults(func=cmd_sweep)

    p_duel = sub.add_parser("duel", help="Monte Carlo duel simulation with cooldowns, Ki, and hit chance.")
    add_common_fighter_args(p_duel, "attacker")
    add_common_fighter_args(p_duel, "defender")
    p_duel.add_argument("--attacker-rotation", default="kame_wave,ki_blast,vanish_strike")
    p_duel.add_argument("--defender-rotation", default="guard,kame_wave,ki_blast")
    p_duel.add_argument("--duration", type=float, default=30.0)
    p_duel.add_argument("--iterations", type=int, default=200)
    p_duel.add_argument("--seed", type=int, default=7)
    p_duel.add_argument("--tech-mastery-mode", choices=("zero", "linear", "focused", "veteran"), default="linear")
    p_duel.add_argument("--ki-regen-per-sec", type=float, default=0.0, help="Optional simplified Ki regen.")
    p_duel.add_argument("--include-samples", type=int, default=0, help="Include N sample timelines in output.")
    p_duel.add_argument("--json", action="store_true")
    p_duel.set_defaults(func=cmd_duel)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()

