"""
DB vertical-slice character typeclass.
"""

from __future__ import annotations

import random
import time

from evennia import search_tag
from evennia.objects.objects import DefaultCharacter

from world.color_utils import colorize
from world.events import emit_entity_delta
from world.power import compute_current_pl
from world.racials import ensure_character_racials
from world.techniques import STARTER_TECHNIQUES

from .objects import ObjectParent

CHARGEN_STEPS = [
    ("race",       "Race",       "Enter your race:"),
    ("sex",        "Sex",        "Choose sex [male/female/other]:"),
    ("hair_style", "Hair Style", "Enter a hair style (e.g. spiky, short, ponytail, bald):"),
    ("hair_color", "Hair Color", "Enter a hair color (e.g. black, blond, red, white):"),
    ("eye_color",  "Eye Color",  "Enter an eye color (e.g. black, blue, red, green):"),
    ("aura_color", "Aura Color", "Enter your aura color (e.g. white, gold, blue, green):"),
]

# Descriptive mapping for menu display - maps internal keys to display names
RACE_DISPLAY_NAMES = {
    "saiyan":     "|ySaiyan|n      — Warrior race with exponential growth. Zenkai after defeat.",
    "half_breed": "|yHalf-Breed|n  — Hybrid latent power that erupts beyond expectation.",
    "human":      "|wHuman|n       — Relentless potential. Mastery and grit exceed all limits.",
    "namekian":   "|gNamekian|n    — Ancient regenerators with deep spiritual ki.",
    "majin":      "|mMajin|n       — Malleable, resilient, and completely unpredictable.",
    "android":    "|cAndroid|n     — Cold efficiency and superior energy management.",
    "biodroid":   "|mBiodroid|n    — Adaptive predator that evolves to overcome any foe.",
    "frost_demon":"|bFrost Demon|n — Ruthless rulers with precision and iron control.",
    "grey":       "|xGrey|n        — Immovable tacticians who dominate by sheer willpower.",
    "kai":        "|yKai|n         — Divine guardians attuned to sacred ki.",
    "truffle":    "|cTruffle|n     — Tech specialists who weaponize intellect.",
}

# Race options for character creation
RACE_OPTIONS = {
    "saiyan",
    "human",
    "namekian",
    "frost_demon",
    "android",
    "bio_android",
    "biodroid",
    "majin",
    "half_breed",  # Human/Saiyan hybrid
    "truffle",
    "grey",  # Jiren race
    "kai",
}
SEX_OPTIONS = {"male", "female", "other"}


class Character(ObjectParent, DefaultCharacter):
    """
    Character with PL, combat, status, and transformation support.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.race = self.db.race or "saiyan"
        self.db.sex = self.db.sex or "other"
        self.db.hair_style = self.db.hair_style or "spiky"
        self.db.hair_color = self.db.hair_color or "black"
        self.db.eye_color = self.db.eye_color or "black"
        self.db.skin_color = self.db.skin_color or "light"
        self.db.aura_color = self.db.aura_color or "white"
        self.db.chargen_complete = bool(self.db.chargen_complete)
        self._refresh_sprite_id()
        self.db.base_power = self.db.base_power or 120
        self.db.strength = self.db.strength or 10
        self.db.speed = self.db.speed or 10
        self.db.balance = self.db.balance or 10
        self.db.mastery = self.db.mastery or 10
        self.db.ki_control = self.db.ki_control or 5
        self.db.hp_max = self.db.hp_max or 120
        self.db.hp_current = self.db.hp_current or self.db.hp_max
        self.db.ki_max = self.db.ki_max or 90
        self.db.ki_current = self.db.ki_current or int(self.db.ki_max * 0.75)
        self.db.statuses = self.db.statuses or {}
        self.db.combat_target = None
        self.db.in_combat = False
        self.db.is_charging = False
        self.db.charge_stacks = 0
        self.db.suppressed = False
        self.db.suppression_factor = self.db.suppression_factor or 0.35
        self.db.active_form = None
        self.db.form_mastery = self.db.form_mastery or {}
        self.db.unlocked_forms = self.db.unlocked_forms or []
        self.db.tech_mastery = self.db.tech_mastery or {}
        self.db.tech_cooldowns = self.db.tech_cooldowns or {}
        self.db.known_techniques = self.db.known_techniques or list(STARTER_TECHNIQUES)
        self.db.equipped_techniques = self.db.equipped_techniques or list(STARTER_TECHNIQUES[:4])
        self.db.racial_traits = self.db.racial_traits or []
        self.db.lssj_state = self.db.lssj_state or {}
        self.db.coords = self.db.coords or (0, 0, 0)
        # Limb system
        self.db.limbs = self.db.limbs or {
            "left_arm": {"state": "intact", "health": 100},
            "right_arm": {"state": "intact", "health": 100},
            "left_leg": {"state": "intact", "health": 100},
            "right_leg": {"state": "intact", "health": 100},
            "torso": {"state": "intact", "health": 100},
            "head": {"state": "intact", "health": 100},
        }
        self.db.tail = self.db.tail or {"state": "intact", "health": 100}  # For Saiyans
        # Economy
        self.db.zeni = self.db.zeni or 1000  # Starting currency
        self.db.dragon_balls = self.db.dragon_balls or []  # Collected Dragon Balls
        self.db.inventory = self.db.inventory or []  # Equipment/items
        # Guild/Clan
        self.db.guild = self.db.guild or None  # Guild name
        self.db.guild_rank = self.db.guild_rank or None  # Member, Officer, Leader
        ensure_character_racials(self)

    def at_post_puppet(self, **kwargs):
        super().at_post_puppet(**kwargs)
        self._ensure_profile_defaults()
        emit_entity_delta(self)
        
        # ═══════════════════════════════════════════════════════════════
        # FIRST LOGIN EXPERIENCE - The "WOW" Factor
        # ═══════════════════════════════════════════════════════════════
        first_login = not self.attributes.has('first_login_done')

        if first_login:
            self.db.first_login_done = True
            # ═══════════════════════════════════════════════════════════════
            # SPAWN NEW CHARACTERS ON KAME ISLAND
            # ═══════════════════════════════════════════════════════════════
            try:
                from world.build_kame_island import get_kame_island_start
                kame_start = get_kame_island_start()
                if kame_start:
                    self.location = kame_start
                    self.msg("|g★ You arrive at Kame Island!|n")
            except Exception:
                pass

            # Run chargen for characters that haven't completed it
            # (text-client players; web UI players have it pre-filled via setrace)
            if not self.db.chargen_complete:
                self.start_chargen()
                return  # chargen takes over input; skip the welcome splash

            self._do_first_login_experience()
        
        # Check if Metamoran fusion has expired while away
        from world.fusions import check_and_handle_fusion_expiry
        was_expired, msg = check_and_handle_fusion_expiry(self)
        if was_expired:
            self.msg(f"|r{msg}|n")
        try:
            from world.events import emit_map_data
            coords = getattr(self.db, "coords", (0, 0, 0))
            if coords:
                emit_map_data(self, coords[0], coords[1], radius=7)
        except Exception:
            pass

    def _do_first_login_experience(self):
        """EPIC first login experience that shows we're serious."""
        from world.power import compute_current_pl
        pl, _ = compute_current_pl(self)
        
        # ═══════════════════════════════════════════════════════════════
        # THE ARRIVAL - Cinematic intro
        # ═══════════════════════════════════════════════════════════════
        intro = """


╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ ███╗   ██╗    ║
║  ██╔════╝ ██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗████╗  ██║    ║
║  ██║  ███╗██║   ██║██████╔╝   ██║   █████╗  ██║   ██║██╔██╗ ██║    ║
║  ██║   ██║██║   ██║██╔══██╗   ██║   ██╔══╝  ██║   ██║██║╚██╗██║    ║
║  ╚██████╔╝╚██████╔╝██║  ██║   ██║   ███████╗╚██████╔╝██║ ╚████║    ║
║   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝    ║
║                                                                      ║
║   ██████╗ ███████╗██╗   ██╗██╗  ████████╗███████╗                    ║
║  ██╔════╝ ██╔════╝██║   ██║██║  ╚══██╔══╝██╔════╝                    ║
║  ██║  ███╗█████╗  ██║   ██║██║     ██║   █████╗                      ║
║  ██║   ██║██╔══╝  ╚██╗ ██╔╝██║     ██║   ██╔══╝                      ║
║  ╚██████╔╝███████╗ ╚████╔╝ ███████╗██║   ███████╗                    ║
║   ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝   ╚══════╝                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

        |g★|n Welcome to Earth, Warrior.

        |yYour journey begins now.|n
        """
        self.msg(intro)
        
        # Show their power and make them feel special
        power_msg = f"""

╔══════════════════════════════════════════════════════════════════════╗
║                       ⚡ YOUR POTENTIAL ⚡                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   Name:   |w{self.key}|n                                                 ║
║   Race:   |c{self.db.race}|n                                             ║
║   Power:  |r{pl:,}|n                                                ║
║                                                                      ║
║   |y★ Your power level is merely a number. What matters is your heart.|n ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        self.msg(power_msg)
        
        # Give them immediate direction
        directions = """

╔══════════════════════════════════════════════════════════════════════╗
║                    ★ YOUR TRAINING BEGINS ★                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   |g►|n  Type |wlook|n to see your surroundings                             ║
║   |g►|n  Type |w+stats|n to view your full stats                            ║
║   |g►|n  Type |whelp|n for commands                                       ║
║   |g►|n  Type |wquest|n to see available missions                          ║
║   |g►|n  Find a |yTrainer|n to learn techniques                          ║
║   |g►|n  Go |wnorth|n to find training areas                            ║
║                                                                      ║
║   |r⚡ YOUR NEXT STEPS:|n                                           ║
║   |g►|n  Meet Master Roshi inside Kame House - he has quests!        ║
║   |g►|n  Try the |wTraining Dummy|n in the Training Grounds!            ║
║   |g►|n  Type |wlook|n to see where you are, |whelp|n for commands.         ║
║   |g►|n  Go to the |wDock|n and type |wboat|n to travel to Earth!           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        self.msg(directions)
        
        # Give them a starter technique immediately!
        known = self.db.known_techniques or []
        if 'ki_blast' not in known:
            known.append('ki_blast')
            self.db.known_techniques = known
            self.msg("""

╔══════════════════════════════════════════════════════════════════════╗
║                    ★ TECHNIQUE UNLOCKED ★                           ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   |y✦ KI BLAST|n                                                      ║
║   You've instinctively learned to fire a basic ki blast!            ║
║                                                                      ║
║   |g►|n  Type |wtech ki_blast|n to test it!                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
            """)
        
        # Auto-give some zeni for their first day
        if not self.db.zeni or self.db.zeni < 100:
            self.db.zeni = 500
            self.msg("""

|g★ You received 500zeni from your first day of training!|n
            """)

    def at_post_unpuppet(self, account, **kwargs):
        """Called just after disconnecting account<->object link."""
        # Auto-unfuse when logging out so partner doesn't get stuck
        from world.fusions import is_fused, unfuse, get_fusion_partner
        if is_fused(self):
            ok, msg = unfuse(self)
            # Try to notify the partner if they're online
            partner_id = get_fusion_partner(self)
            if partner_id:
                from evennia import search_object
                partner_objs = search_object(partner_id)
                if partner_objs:
                    partner = partner_objs[0]
                    partner.msg(f"|yYour fusion partner {self.key} logged out. The fusion has ended.|n")

    def at_post_move(self, source_location, move_type="move", **kwargs):
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        self._ensure_profile_defaults()
        emit_entity_delta(self)
        try:
            from world.events import emit_map_data
            coords = getattr(self.db, "coords", (0, 0, 0))
            if coords:
                emit_map_data(self, coords[0], coords[1], radius=7)
        except Exception:
            pass

    def execute_cmd(self, raw_string, session=None, **kwargs):
        """
        Intercept input for explicit modal IC flows (chargen, codex/info menus).
        """
        self._ensure_profile_defaults()
        if self.has_account and getattr(self.ndb, "info_menu_state", None):
            text = (raw_string or "").strip()
            if text.lower() in {"quit", "@quit"}:
                return super().execute_cmd(raw_string, session=session, **kwargs)
            try:
                from commands.db_commands import handle_ic_info_menu_input

                if handle_ic_info_menu_input(self, text):
                    return
            except Exception:
                # Fall through to normal command handling on menu-routing errors.
                pass
        if self.has_account and self._is_ic_chargen_active():
            text = (raw_string or "").strip()
            if text.lower() in {"quit", "@quit"}:
                return super().execute_cmd(raw_string, session=session, **kwargs)
            self._process_chargen_input(text)
            return
        return super().execute_cmd(raw_string, session=session, **kwargs)

    def _ensure_profile_defaults(self):
        changed = False
        defaults = {
            "sex": "other",
            "hair_style": "spiky",
            "hair_color": "black",
            "eye_color": "black",
            "skin_color": "light",
            "aura_color": "white",
        }
        if not self.attributes.has("chargen_complete"):
            # New character — chargen is pending (triggered in at_post_puppet on first login)
            self.db.chargen_complete = False
            changed = True
        if not self.attributes.has("chargen_active"):
            self.db.chargen_active = False
            changed = True
        for key, value in defaults.items():
            if not self.attributes.has(key):
                setattr(self.db, key, value)
                changed = True
        if not self.attributes.has("race"):
            self.db.race = "saiyan"
            changed = True
        if not self.attributes.has("unlocked_forms"):
            self.db.unlocked_forms = []
            changed = True
        if not self.attributes.has("racial_traits"):
            self.db.racial_traits = []
            changed = True
        if not self.attributes.has("lssj_state"):
            self.db.lssj_state = {}
            changed = True
        ensure_character_racials(self)
        if changed or not self.db.sprite_id:
            self._refresh_sprite_id()

    def _refresh_sprite_id(self):
        race = (self.db.race or "humanoid").lower().replace(" ", "_")
        sex = (self.db.sex or "other").lower().replace(" ", "_")
        # Use the animated walk cycle sprite for players
        self.db.sprite_id = f"saiyan_warrior_walk_cycle"

    def _chargen_step_index(self):
        return int(self.db.chargen_step_index or 0)

    def _is_ic_chargen_active(self):
        return bool(self.has_account and not self.db.chargen_complete and self.db.chargen_active)

    def start_chargen(self):
        self.db.chargen_active = True
        self.db.chargen_step_index = 0
        self.msg("""
|y╔══════════════════════════════════════════════════════════╗
║           ★  CHARACTER CREATION  ★                      ║
╠══════════════════════════════════════════════════════════╣
║  Answer each prompt to shape your warrior's identity.   ║
║  Type |wcancel|y at any time to accept all current defaults. ║
╚══════════════════════════════════════════════════════════╝|n
""")
        self._show_chargen_prompt()

    def _show_chargen_prompt(self):
        idx = self._chargen_step_index()
        if idx >= len(CHARGEN_STEPS):
            self.finish_chargen()
            return
        key, label, prompt = CHARGEN_STEPS[idx]
        current_val = getattr(self.db, key, "") or ""
        step_of = f"Step {idx + 1}/{len(CHARGEN_STEPS)}"

        header = f"|y[ {step_of} — {label} ]|n"
        self.msg(f"\n{header}")

        # Race step gets a special formatted list
        if key == "race":
            self.msg("|xChoose your race — each has unique racial traits:|n\n")
            for race_key, desc in RACE_DISPLAY_NAMES.items():
                self.msg(f"  |w{race_key:<12}|n  {desc}")
            self.msg(f"\n|w{prompt}|n |x(current: {current_val or 'none'})|n")
        else:
            preview = colorize(current_val) if "color" in key else current_val
            self.msg(f"|w{prompt}|n |x(current: {preview or 'none'})|n")

    def _normalize_chargen_value(self, key, value):
        value = (value or "").strip()
        if not value:
            return None, "Please enter a value."
        if key in {"hair_style", "hair_color", "eye_color", "aura_color"}:
            cleaned = value.lower().replace("-", "_").replace(" ", "_")
            if len(cleaned) > 24:
                return None, "Keep it under 24 characters."
            return cleaned, None
        if key == "race":
            cleaned = value.lower().replace(" ", "_")
            if cleaned not in RACE_OPTIONS:
                return None, f"Invalid race. Choose: {', '.join(sorted(RACE_OPTIONS))}"
            return cleaned, None
        if key == "sex":
            cleaned = value.lower()
            if cleaned not in SEX_OPTIONS:
                return None, f"Invalid sex. Choose: {', '.join(sorted(SEX_OPTIONS))}"
            return cleaned, None
        return value, None

    def _process_chargen_input(self, text):
        if not text:
            self._show_chargen_prompt()
            return
        if text.lower() == "cancel":
            self.finish_chargen()
            return
        idx = self._chargen_step_index()
        if idx >= len(CHARGEN_STEPS):
            self.finish_chargen()
            return
        key, label, _prompt = CHARGEN_STEPS[idx]
        value, error = self._normalize_chargen_value(key, text)
        if error:
            self.msg(f"|r{error}|n")
            self._show_chargen_prompt()
            return
        setattr(self.db, key, value)
        self.db.chargen_step_index = idx + 1
        shown = colorize(value) if "color" in key else value
        self.msg(f"|gSet {label} to {shown}|g.|n")
        self._show_chargen_prompt()

    def finish_chargen(self):
        self.db.chargen_complete = True
        self.db.chargen_active = False
        self.db.chargen_step_index = 0
        self._refresh_sprite_id()
        ensure_character_racials(self)
        race = (self.db.race or "unknown").replace("_", " ").title()
        sex  = (self.db.sex  or "other").title()
        self.msg(f"""
|g╔══════════════════════════════════════════════════════════╗
║              ★  WARRIOR FORGED  ★                       ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Race  : |w{race:<20}|g                              ║
║  Sex   : |w{sex:<20}|g                              ║
║  Hair  : |w{self.db.hair_style} ({colorize(self.db.hair_color)}|g)|w{"":>10}|g                  ║
║  Eyes  : |w{colorize(self.db.eye_color)}|g                                            ║
║  Aura  : |w{colorize(self.db.aura_color)}|g                                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝|n
""")
        emit_entity_delta(self)
        self._do_first_login_experience()

    def get_current_pl(self):
        return compute_current_pl(self)

    def get_stats(self):
        pl, breakdown = self.get_current_pl()
        return {
            "hp_current": self.db.hp_current,
            "hp_max": self.db.hp_max,
            "ki_current": self.db.ki_current,
            "ki_max": self.db.ki_max,
            "power_level": pl,
            "displayed_power_level": breakdown["displayed_pl"],
            "base_power": self.db.base_power,
            "strength": self.db.strength,
            "speed": self.db.speed,
            "balance": self.db.balance,
            "mastery": self.db.mastery,
            "ki_control": self.db.ki_control,
        }

    def clean_statuses(self):
        now = time.time()
        statuses = dict(self.db.statuses or {})
        dirty = False
        for key, data in list(statuses.items()):
            until = data.get("until")
            if until and until <= now:
                statuses.pop(key, None)
                dirty = True
        if dirty:
            self.db.statuses = statuses
        return statuses

    def has_status(self, key):
        return key in self.clean_statuses()

    def add_status(self, key, duration, **data):
        statuses = self.clean_statuses()
        statuses[key] = {"until": time.time() + float(duration), "data": data}
        self.db.statuses = statuses

    def remove_status(self, key):
        statuses = self.clean_statuses()
        if key in statuses:
            statuses.pop(key, None)
            self.db.statuses = statuses

    def get_status_data(self, key, default=None):
        return self.clean_statuses().get(key, {}).get("data", default)

    def is_in_combat(self):
        return bool(self.db.in_combat and self.db.combat_target)

    def spend_ki(self, amount):
        amount = int(max(0, amount))
        if (self.db.ki_current or 0) < amount:
            return False
        self.db.ki_current = max(0, (self.db.ki_current or 0) - amount)
        emit_entity_delta(self)
        return True

    def restore_ki(self, amount):
        amount = int(max(0, amount))
        self.db.ki_current = min(self.db.ki_max, (self.db.ki_current or 0) + amount)
        emit_entity_delta(self)
        return self.db.ki_current

    def _get_safe_room(self):
        safe_rooms = search_tag("safe_room", category="zone")
        if self.location and self.location in safe_rooms:
            return self.location
        return safe_rooms[0] if safe_rooms else self.home

    def apply_damage(self, amount, source=None, kind="attack"):
        amount = int(max(0, amount))
        
        # Set counter window for the defender (they can counter within 2 seconds)
        import time
        if source and source != self:
            self.db.last_attacker = source
            self.db.counter_window = time.time()
        
        # Apply guard reduction
        if self.has_status("guard"):
            reduction = self.get_status_data("guard", {}).get("reduction", 0.45)
            amount = max(1, int(amount * (1.0 - reduction)))
        if self.has_status("afterimage") and random.random() < 0.5:
            self.remove_status("afterimage")
            if self.location:
                self.location.msg_contents(f"{self.key} blurs with an afterimage and avoids the hit!")
            return 0
        self.db.hp_current = max(0, (self.db.hp_current or 0) - amount)
        
        # Check for Rage Mode activation (auto at <20% HP)
        if self.db.hp_current > 0:
            max_hp = self.db.hp_max or 1
            hp_percent = self.db.hp_current / max_hp
            
            # Activate rage if below 20% and not already in rage
            if hp_percent < 0.20 and not self.has_status("rage"):
                self.add_status("rage", 10, damage_boost=1.5)
                self.msg("|r>>> RAGE MODE ACTIVATED! <<<|n You feel your power surge as anger takes over!")
                if self.location:
                    self.location.msg_contents(f"{self.key} enters a |rblinding rage|!", exclude=self)
        
        if self.db.hp_current <= 0:
            self.handle_defeat(source=source, kind=kind)
        emit_entity_delta(self)
        return amount

    def handle_defeat(self, source=None, kind="attack"):
        from world.combat import disengage, stop_charging

        stop_charging(self, interrupted=True)
        disengage(self)
        self.db.active_form = None
        self.add_status("bruised", 300, pl_penalty=0.92)
        
        # SECURITY: Track defeat history to prevent farming
        now = time.time()
        defeat_history = list(self.db.defeat_history or [])
        # Remove defeats older than 1 hour
        defeat_history = [t for t in defeat_history if now - t < 3600]
        
        # Count recent defeats
        recent_defeat_count = len(defeat_history)
        defeat_history.append(now)
        self.db.defeat_history = defeat_history
        
        # Calculate reward reduction based on defeat frequency
        # More than 3 defeats in 1 hour = farming detected
        if recent_defeat_count >= 5:
            reward_reduction = 0.0  # 100% reduction - no rewards
        elif recent_defeat_count >= 3:
            reward_reduction = 0.5  # 50% reduction
        else:
            reward_reduction = 1.0  # Full rewards
        
        # Apply reduced rewards based on farming detection
        self.db.hp_current = max(1, int(self.db.hp_max * 0.55 * reward_reduction))
        self.db.ki_current = max(1, int(self.db.ki_max * 0.40 * reward_reduction))
        
        # Zenkai Boost for Saiyans - reduced/f disabled if farming
        race = (self.db.race or "").lower()
        if race in {"saiyan", "half_breed"} and reward_reduction > 0:
            # Track zenKai boost count
            zenkai_count = getattr(self.db, 'zenkai_count', 0) or 0
            self.db.zenkai_count = zenkai_count + 1
            
            # Calculate zenkai bonus (diminishing returns) with reduction
            zenkai_bonus = min(0.15, 0.04 + (zenkai_count * 0.01)) * reward_reduction
            
            if zenkai_bonus > 0.02:  # Only give meaningful bonuses
                # Add temporary zenkai status
                self.add_status("zenkai_boost", 600, pl_bonus=1.0 + zenkai_bonus)  # 10 minutes
                self.msg(f"|g>>> ZENKAI BOOST! <<<|n You feel stronger after recovering! (+{zenkai_bonus*100:.0f}% PL for 10 min)")
            else:
                self.msg("|gYou recover from defeat but feel no significant power increase.|n")
        elif race in {"saiyan", "half_breed"}:
            self.msg("|gYou recover from defeat but your body is too exhausted to grow stronger.|n")
        
        # Regeneration for Namekians/Majins/Biodroids - reduced if farming
        if race in {"namekian", "majin", "biodroid"} and reward_reduction > 0:
            regen_bonus = getattr(self.db, 'regen_level', 0) or 0
            regen_heal = int(self.db.hp_max * (0.08 + regen_bonus * 0.02) * reward_reduction)
            self.db.hp_current = min(self.db.hp_max, self.db.hp_current + regen_heal)
            self.db.regen_level = regen_bonus + 1
        elif race in {"namekian", "majin", "biodroid"}:
            self.msg("|gYour regeneration is exhausted from repeated defeats.|n")
        
        # Notify player if farming is detected
        if recent_defeat_count >= 3:
            self.msg("|rWARNING: You are defeating too frequently. Rewards reduced to prevent exploitation.|n")
        
        safe_room = self._get_safe_room()
        if safe_room:
            self.move_to(safe_room, quiet=True)
        if source:
            self.msg(f"|rYou were defeated by {source.key}. You wake up bruised at a safe point.|n")
        else:
            self.msg("|rYou were defeated. You wake up bruised at a safe point.|n")
        emit_entity_delta(self)

    def get_limb_state(self, limb_key):
        """Get the state of a specific limb."""
        limbs = self.db.limbs or {}
        return limbs.get(limb_key, {}).get("state", "intact")

    def damage_limb(self, limb_key, damage, source=None):
        """Apply damage to a limb. Returns True if limb was lost."""
        limbs = dict(self.db.limbs or {})
        if limb_key not in limbs:
            return False
        
        limb = limbs[limb_key]
        current_health = limb.get("health", 100)
        new_health = max(0, current_health - damage)
        
        # Determine new state
        old_state = limb.get("state", "intact")
        if new_health <= 0:
            new_state = "lost"
        elif new_health < 50:
            new_state = "broken"
        elif new_health < 100:
            new_state = "damaged"
        else:
            new_state = "intact"
        
        limbs[limb_key] = {"state": new_state, "health": new_health}
        self.db.limbs = limbs
        
        # Apply penalties for damaged limbs
        if new_state == "broken" or new_state == "lost":
            self._apply_limb_penalty(limb_key)
        
        # Message about limb damage
        if new_state == "lost" and old_state != "lost":
            self.msg(f"|r>>> {limb_key.replace('_', ' ').title()} LOST! <<<|n")
            if self.location:
                self.location.msg_contents(f"{self.key}'s {limb_key.replace('_', ' ')} is severed!", exclude=self)
        elif new_state == "broken" and old_state != "broken":
            self.msg(f"|r>>> {limb_key.replace('_', ' ').title()} BROKEN! <<<|n")
        
        return new_state == "lost"

    def _apply_limb_penalty(self, limb_key):
        """Apply combat penalties for broken/lost limbs."""
        penalties = {
            "left_arm": {"damage": 0.15},
            "right_arm": {"damage": 0.15},
            "left_leg": {"speed": 0.20},
            "right_leg": {"speed": 0.20},
            "torso": {"defense": 0.15},
            "head": {"all": 0.25},
        }
        penalty = penalties.get(limb_key, {})
        if penalty:
            self.add_status(f"limb_{limb_key}_penalty", 300, **penalty)

    def regenerate_limb(self, limb_key):
        """Regenerate a lost/damaged limb. Returns success."""
        limbs = dict(self.db.limbs or {})
        if limb_key not in limbs:
            return False
        
        limb = limbs[limb_key]
        current_state = limb.get("state", "intact")
        
        if current_state == "intact":
            return True  # Already fine
        
        # Namekians regenerate instantly
        race = (self.db.race or "").lower()
        if race == "namekian":
            limbs[limb_key] = {"state": "intact", "health": 100}
            self.db.limbs = limbs
            self.msg(f"|g>>> {limb_key.replace('_', ' ').title()} REGENERATED! <<<|n")
            return True
        
        # Majins and Biodroids regenerate slowly
        if race in {"majin", "biodroid"}:
            limbs[limb_key] = {"state": "damaged", "health": 60}
            self.db.limbs = limbs
            self.msg(f"|gYour {limb_key.replace('_', ' ')} slowly regenerates.|n")
            return True
        
        # Other races can't regenerate limbs naturally
        return False

    def heal_all_limbs(self):
        """Fully heal all limbs - used by items/healing chambers."""
        limbs = self.db.limbs or {}
        for key in limbs:
            limbs[key] = {"state": "intact", "health": 100}
        self.db.limbs = limbs
        # Clear limb penalties
        for status_key in list(self.db.statuses or {}):
            if status_key.startswith("limb_"):
                self.remove_status(status_key)
        self.msg("|gAll limbs fully healed!|n")
