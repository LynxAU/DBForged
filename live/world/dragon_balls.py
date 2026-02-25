"""
Dragon Ball System - DBForged Bible Implementation
================================================
Implements Dragon Ball collection and Shenron wish system.
"""

import time
import random


# Shenron ASCII Art
SHENRON_ART = """
                    /`.
                  / / `.                 .-.
                 / /   `.               ( @ @)
                 | |     `..___________..'   }
                 | |      ,'             `.  }
                 | |    ,'                 `}
                 |_|---'                     }
                 |_|                        }
                 |_|      |`.              }
                 |_|     |  `...          }
                 |_|    |      `.......  }
                 |_|   |           ---'}
                 |_|  |            __.' }
                /|_|  |         __.'  }
                / |_|  |______..'     }
               /  |___|            ___}
              /   |____|          /  }
             /    |              /   }
            /_____|             /    }
           /______/            /     }
          /      /            /      }
         /______/            /       }
        /      /            /        }
       /______/            /         }
      /      /            /          }
     /______/            /           }
    /      /            /            }
   /______/     _....._              }
  /      /    .'       `.___        }
 /______/   .'           ___ `.___ }
                      .'   `-..-'`
                     (     ____)
                      `..'    `)
                        `....'
"""


# Wish definitions
WISHES = {
    "1": {
        "name": "Power Boost",
        "desc": "Increase your Power Level by 50%",
        "effect": "pl_boost"
    },
    "2": {
        "name": "Stat Increase",
        "desc": "Increase all stats by 20%",
        "effect": "stat_boost"
    },
    "3": {
        "name": "Unlock Transformation",
        "desc": "Unlock a random transformation you qualify for",
        "effect": "unlock_form"
    },
    "4": {
        "name": "Heal Full",
        "desc": "Restore HP and KI to full",
        "effect": "full_heal"
    },
    "5": {
        "name": "Revive Ally",
        "desc": "Revive a fallen player or NPC",
        "effect": "revive"
    },
    "6": {
        "name": "Knowledge",
        "desc": "Gain 100% bonus XP for your next level",
        "effect": "xp_boost"
    },
}


def check_dragon_ball_collection(character):
    """
    Check how many Dragon Balls the character has collected.
    Returns the count (0-7).
    """
    collected = getattr(character.db, 'dragon_balls_collected', [])
    return len(collected)


def add_dragon_ball(character, ball_number):
    """
    Add a Dragon Ball to character's collection.
    Returns True if all 7 collected.
    """
    if not 1 <= ball_number <= 7:
        return False
    
    collected = getattr(character.db, 'dragon_balls_collected', [])
    
    if ball_number in collected:
        return False  # Already have this one
    
    collected.append(ball_number)
    character.db.dragon_balls_collected = collected
    
    # Check if all 7 collected
    if len(collected) == 7:
        character.msg("|cYou have collected all 7 Dragon Balls! Type 'summon_shenron' to call forth the eternal dragon!|n")
        return True
    
    character.msg(f"|cYou collected Dragon Ball #{ball_number}! ({len(collected)}/7)|n")
    return False


def can_summon_shenron(character):
    """Check if character can summon Shenron."""
    collected = getattr(character.db, 'dragon_balls_collected', [])
    return len(collected) >= 7


def summon_shenron(character):
    """
    Summon Shenron when all 7 Dragon Balls are collected.
    Returns the Shenron appearance message.
    """
    if not can_summon_shenron(character):
        return False, "You need all 7 Dragon Balls to summon Shenron."
    
    # Clear Dragon Balls (they're used up)
    character.db.dragon_balls_collected = []
    character.db.shenron_active = True
    character.db.shenron_wishes_remaining = 5
    character.db.shenron_summon_time = time.time()
    
    return True, f"""
|c===== SHENRON APPEARS! =====|n
{SHENRON_ART}
|cThe eternal dragon Shenron coils before you, awaiting your wishes.|n
You have 5 wishes remaining!|n
|c==============================|n
Use 'wish <number>' to make a wish:
  1. Power Boost (+50% PL)
  2. Stat Increase (+20% all stats)
  3. Unlock Transformation
  4. Heal Full (restore HP/KI)
  5. Revive Ally
  6. Knowledge (+100% XP)
"""


def make_wish(character, wish_number):
    """
    Make a wish from Shenron.
    """
    if not getattr(character.db, 'shenron_active', False):
        return False, "Shenron is not currently summoned."
    
    wishes_remaining = character.db.shenron_wishes_remaining or 0
    if wishes_remaining <= 0:
        return False, "You have no wishes remaining."
    
    wish_data = WISHES.get(str(wish_number))
    if not wish_data:
        return False, "Invalid wish number. Choose 1-6."
    
    # Apply the wish
    success, message = apply_wish_effect(character, wish_data['effect'])
    
    if success:
        character.db.shenron_wishes_remaining = wishes_remaining - 1
        wishes_left = character.db.shenron_wishes_remaining
        
        message += f"\n|cYou have {wishes_left} wish(s) remaining.|n"
        
        # Check if Shenron should depart
        if wishes_left <= 0:
            dismiss_shenron(character)
            message += "\n|cShenron departs, his task complete...|n"
    
    return success, message


def apply_wish_effect(character, effect_type):
    """Apply the effect of a wish."""
    
    if effect_type == "pl_boost":
        current_pl = character.db.power_level or 100
        new_pl = int(current_pl * 1.5)
        character.db.power_level = new_pl
        return True, f"|cYour power level increases from {current_pl} to {new_pl}!|n"
    
    elif effect_type == "stat_boost":
        # Boost various stats by 20%
        stats = ['strength', 'speed', 'defense', 'ki_power']
        for stat in stats:
            current = getattr(character.db, stat, 10) or 10
            setattr(character.db, stat, int(current * 1.2))
        return True, f"|cAll your stats increase by 20%!|n"
    
    elif effect_type == "unlock_form":
        # Find a form the character qualifies for but doesn't have
        from world.forms import FORMS
        unlocked = getattr(character.db, 'unlocked_forms', [])
        
        # Find a form they don't have
        available = []
        pl = character.db.power_level or 100
        for form_id, form_data in FORMS.items():
            if form_id not in unlocked:
                prereq = form_data.get('prerequisites', {})
                req_pl = prereq.get('power_level', 0)
                if pl >= req_pl:
                    available.append(form_id)
        
        if available:
            # Unlock a random available form
            import random
            form_to_unlock = random.choice(available)
            unlocked.append(form_to_unlock)
            character.db.unlocked_forms = unlocked
            form_name = FORMS[form_to_unlock].get('name', form_to_unlock)
            return True, f"|cYou unlock the {form_name} transformation!|n"
        else:
            return False, "You don't qualify for any new transformations."
    
    elif effect_type == "full_heal":
        hp_max = character.db.hp_max or 100
        ki_max = character.db.ki_max or 100
        character.db.hp_current = hp_max
        character.db.ki_current = ki_max
        return True, f"|cYour HP and KI are fully restored!|n"
    
    elif effect_type == "revive":
        # This would need a target - simplified for now
        hp_max = character.db.hp_max or 100
        character.db.hp_current = int(hp_max * 0.5)
        return True, f"|cYou feel revitalized! (HP restored to 50%)|n"
    
    elif effect_type == "xp_boost":
        character.db.xp_boost_pending = True
        return True, f"|cYou feel enlightened! Your next level grants double XP!|n"
    
    return False, "Unknown wish effect."


def dismiss_shenron(character):
    """Dismiss Shenron after all wishes are used."""
    character.db.shenron_active = False
    character.db.shenron_wishes_remaining = 0


def get_dragon_ball_status(character):
    """Get Dragon Ball collection status."""
    collected = getattr(character.db, 'dragon_balls_collected', [])
    
    status = {
        'collected': sorted(collected),
        'count': len(collected),
        'shenron_active': getattr(character.db, 'shenron_active', False),
        'wishes_remaining': getattr(character.db, 'shenron_wishes_remaining', 0),
    }
    
    return status
