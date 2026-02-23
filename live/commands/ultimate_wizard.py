"""
DBForged Custom Ultimate Creator Wizard

This module provides an Evennia EvMenu-based wizard for players
to create their own signature ultimate technique.
"""

from evennia.utils.evmenu import EvMenu
from world.color_utils import colorize

# Attack types available for custom ultimates
ATTACK_TYPES = {
    "beam": {
        "name": "Beam",
        "description": "A concentrated stream of energy fired from your hands",
        "flavor_template": "You cup your hands forward, palms facing {target}. Energy swirls between your fingers as you gather your power. With a roar of \"{name}!\" you unleash a blazing {color_name} beam straight at {target}!",
    },
    "disk": {
        "name": "Energy Disk",
        "description": "A razor-sharp spinning disc of concentrated energy",
        "flavor_template": "You form your hands into a cutting motion, fingers spread. A spinning {color_name} disc materializes between your hands. You swipe forward and send the razor-sharp disk hurtling toward {target}!",
    },
    "ball": {
        "name": "Energy Ball",
        "description": "A large orb of concentrated ki energy",
        "flavor_template": "You hold both hands out in front of you, palms facing each other. You scream \"{name}!\" as a massive swirling {color_name} orb of energy forms between your palms. Rocks begin to lift around you as the power builds, then you thrust forward with another scream - the ball rockets toward {target} with a deafening BOOM!",
    },
    "wave": {
        "name": "Energy Wave",
        "description": "A sweeping wave of energy that crashes across the area",
        "flavor_template": "You plant your feet and raise your hands to the sky. A {color_name} aura surrounds you as you gather immense power. With a final cry of \"{name}!\" you thrust both hands forward, unleashing a massive energy wave that sweeps across everything in its path!",
    },
    "rush": {
        "name": "Rush Attack",
        "description": "A devastating close-combo assault",
        "flavor_template": "You rocket forward at incredible speed, your entire body engulfed in {color_name} energy. \"{name}!\" you scream as you close the distance in an instant, slamming into {target} with a barrage of strikes that culminates in one devastating final blow!",
    },
    "spear": {
        "name": "Energy Spear",
        "description": "A focused beam condensed into a piercing lance",
        "flavor_template": "You focus all your energy into a single point, your finger pointing at {target}. The air itself seems to tear as a {color_name} lance of pure energy forms. \"{name}!\" you shout as you release - the spear pierces through everything in its path!",
    },
}

# Energy colors available
ENERGY_COLORS = {
    "blue": {"name": "Azure Blue", "color_code": "c"},
    "red": {"name": "Crimson Red", "color_code": "r"},
    "green": {"name": "Emerald Green", "color_code": "g"},
    "yellow": {"name": "Golden Yellow", "color_code": "y"},
    "purple": {"name": "Violet Purple", "color_code": "m"},
    "white": {"name": "Pure White", "color_code": "w"},
    "orange": {"name": "Burning Orange", "color_code": "y"},
    "pink": {"name": "Hot Pink", "color_code": "m"},
}


def _get_wizard_data(caller, session):
    """Get or initialize ultimate wizard data"""
    state = caller.ndb._evmenu_state if hasattr(caller, 'ndb') and hasattr(caller.ndb, '_evmenu_state') else {}
    if "ultimate_wizard" not in state:
        state["ultimate_wizard"] = {}
    return state["ultimate_wizard"]


def _save_wizard_data(caller, key, value):
    """Save ultimate wizard data field"""
    if not hasattr(caller.ndb, '_evmenu_state'):
        caller.ndb._evmenu_state = {}
    if "ultimate_wizard" not in caller.ndb._evmenu_state:
        caller.ndb._ultimate_wizard = {}
    caller.ndb._ultimate_wizard[key] = value


def _get_wizard_data_safe(caller):
    """Safely get wizard data from character or account"""
    # Try character first
    if hasattr(caller, 'db') and caller.db:
        return caller.db.ultimate_wizard or {}
    # Fall back to ndb
    if hasattr(caller, 'ndb') and hasattr(caller.ndb, '_ultimate_wizard'):
        return caller.ndb._ultimate_wizard
    return {}


def _save_wizard_data_safe(caller, key, value):
    """Safely save wizard data"""
    if hasattr(caller, 'db') and caller.db:
        data = dict(caller.db.ultimate_wizard or {})
        data[key] = value
        caller.db.ultimate_wizard = data
    else:
        if not hasattr(caller, 'ndb'):
            caller.ndb._ultimate_wizard = {}
        caller.ndb._ultimate_wizard[key] = value


def _clear_wizard_data(caller):
    """Clear wizard data"""
    if hasattr(caller, 'db') and caller.db:
        caller.db.ultimate_wizard = {}
    if hasattr(caller, 'ndb') and hasattr(caller.ndb, '_ultimate_wizard'):
        caller.ndb._ultimate_wizard = {}


def _generate_flavor_text(ultimate_data):
    """Generate the full flavor text based on user input"""
    attack_type = ultimate_data.get("attack_type", "beam")
    custom_desc = ultimate_data.get("custom_description", "")
    
    # Get the template
    attack_info = ATTACK_TYPES.get(attack_type, ATTACK_TYPES["beam"])
    template = attack_info["flavor_template"]
    
    # Get color name
    color_key = ultimate_data.get("color", "blue")
    color_info = ENERGY_COLORS.get(color_key, ENERGY_COLORS["blue"])
    color_name = color_info["name"]
    
    # Replace placeholders
    flavor_text = template.format(
        name=ultimate_data.get("name", "Ultimate"),
        color_name=color_name,
        target="{target}"
    )
    
    # If user provided custom description, append or replace
    if custom_desc and custom_desc.strip():
        flavor_text = f"{custom_desc.strip()}\n\n{flavor_text}"
    
    return flavor_text


# Menu nodes
def node_start(caller, session=None):
    """Start the custom ultimate wizard"""
    text = """
|w+-----------------------------------------------------------------------------+
|                        CUSTOM ULTIMATE WIZARD                                 
|+-----------------------------------------------------------------------------+

 Create your own signature ultimate technique!
 
 This wizard will guide you through designing a unique ultimate ability
 that is completely your own.
 
 The ultimate will be stored as your signature technique and can be
 used in combat with the |c/ultimate|n command.
 
 Press |cC|n to cancel at any time.
 Press |cB|n to go back to the previous step.
 
|wReady to begin?|n
"""
    options = [
        {"key": "continue", "desc": "Create my ultimate", "goto": "node_name"}
    ]
    return text, options


def node_name(caller, session=None, input=None):
    """Get the ultimate's name"""
    data = _get_wizard_data_safe(caller)
    
    if input:
        name = input.strip()
        if not name:
            caller.msg("|rPlease enter a name for your ultimate.|n")
            return "node_name", {}
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return "node_name", {}
        if len(name) > 30:
            caller.msg("|rName must be 30 characters or less.|n")
            return "node_name", {}
        
        _save_wizard_data_safe(caller, "name", name)
        return "node_attack_type", {}
    
    text = """
|wStep 1: Name Your Ultimate|n

 What is the name of your signature technique?
 
 Examples: |cFinal Flash|n, |cSpirit Bomb|n, |cNova Strike|n, |cDragon Fist|n
 
 Enter the name below:
"""
    options = []
    return text, options


def node_attack_type(caller, session=None, input=None):
    """Select attack type"""
    data = _get_wizard_data_safe(caller)
    
    if input:
        try:
            choice = int(input.strip())
            types_list = list(ATTACK_TYPES.keys())
            if 1 <= choice <= len(types_list):
                attack_type = types_list[choice - 1]
                _save_wizard_data_safe(caller, "attack_type", attack_type)
                return "node_color", {}
            else:
                caller.msg("|rPlease enter a valid number.|n")
                return "node_attack_type", {}
        except ValueError:
            caller.msg("|rPlease enter a number.|n")
            return "node_attack_type", {}
    
    text = """
|wStep 2: Choose Attack Type|n

 What type of energy attack is it?
 
"""
    # Build options dynamically
    for i, (key, info) in enumerate(ATTACK_TYPES.items(), 1):
        text += f" |c{i}|n - |w{info['name']}|n: {info['description']}\n"
    
    text += "\nEnter the number of your choice:"
    options = []
    return text, options


def node_color(caller, session=None, input=None):
    """Select energy color"""
    data = _get_wizard_data_safe(caller)
    
    if input:
        try:
            choice = int(input.strip())
            colors_list = list(ENERGY_COLORS.keys())
            if 1 <= choice <= len(colors_list):
                color = colors_list[choice - 1]
                _save_wizard_data_safe(caller, "color", color)
                return "node_description", {}
            else:
                caller.msg("|rPlease enter a valid number.|n")
                return "node_color", {}
        except ValueError:
            caller.msg("|rPlease enter a number.|n")
            return "node_color", {}
    
    text = """
|wStep 3: Choose Energy Color|n

 What color is your ultimate technique?
 
"""
    for i, (key, info) in enumerate(ENERGY_COLORS.items(), 1):
        text += f" |c{i}|n - |{info['color_code']}{info['name']}|n\n"
    
    text += "\nEnter the number of your choice:"
    options = []
    return text, options


def node_description(caller, session=None, input=None):
    """Get custom description (optional)"""
    data = _get_wizard_data_safe(caller)
    
    if input is not None:
        # Input is the custom description (can be empty for default)
        custom_desc = input.strip()
        _save_wizard_data_safe(caller, "custom_description", custom_desc)
        return "node_confirm", {}
    
    attack_type = data.get("attack_type", "beam")
    attack_info = ATTACK_TYPES.get(attack_type, ATTACK_TYPES["beam"])
    
    # Get default message for this attack type
    default_msg = attack_info["flavor_template"].format(
        name=data.get("name", "Your Ultimate"),
        color_name=ENERGY_COLORS.get(data.get("color", "blue"), ENERGY_COLORS["blue"])["name"],
        target="{target}"
    )
    
    text = f"""
|wStep 4: Custom Description (Optional)|n

 You can add a custom description to personalize your ultimate's flavor text.
 
 This will appear before the default action description when you use your ultimate.
 
 |yExample:|n
 "With a surge of energy, you concentrate all your power into a single point..."
 
 |yDefault message for your {attack_info['name']}:|n
 "|n{default_msg}|n"
 
 Enter your custom description, or press |cEnter|n to use the default:
"""
    options = []
    return text, options


def node_confirm(caller, session=None, input=None):
    """Confirm and save the ultimate"""
    data = _get_wizard_data_safe(caller)
    
    if input and input.lower() in ["yes", "y", "confirm", "save"]:
        # Save the ultimate to character
        ultimate = {
            "name": data.get("name", "Unnamed Ultimate"),
            "attack_type": data.get("attack_type", "beam"),
            "color": data.get("color", "blue"),
            "custom_description": data.get("custom_description", ""),
            "flavor_text": _generate_flavor_text(data),
        }
        
        # Save to character db
        if hasattr(caller, 'db'):
            caller.db.custom_ultimate = ultimate
            # Also set as equipped ultimate
            caller.db.equipped_ultimate = "custom"
        
        _clear_wizard_data(caller)
        
        text = f"""
|w+-----------------------------------------------------------------------------+
|                        ULTIMATE CREATED!                                      
|+-----------------------------------------------------------------------------+

 Your signature technique has been created!

 |wName:|n {ultimate['name']}
 |wType:|n {ATTACK_TYPES[ultimate['attack_type']]['name']}
 |wColor:|n {ENERGY_COLORS[ultimate['color']]['name']}

 |yFlavor Text Preview:|n
 "{ultimate['flavor_text'].format(target='your target')}"

 Your ultimate is now equipped! Use |c/ultimate <target>|n in combat
 to unleash your signature technique.

|w+-----------------------------------------------------------------------------+
"""
        caller.msg(text)
        return None, {}
    
    # Show confirmation
    attack_type = data.get("attack_type", "beam")
    color = data.get("color", "blue")
    flavor_preview = _generate_flavor_text(data)
    
    text = f"""
|wConfirm Your Ultimate|n

 |wName:|n {data.get('name', 'Unnamed')}
 |wType:|n {ATTACK_TYPES[attack_type]['name']}
 |wColor:|n {ENERGY_COLORS[color]['name']}

 |yFlavor Text Preview:|n
 "{flavor_preview.format(target='your target')}"

 |wConfirm?|n Enter |gyes|n to save, or |gn|n to go back and edit:
"""
    options = [
        {"key": "yes", "desc": "Save my ultimate", "goto": "node_confirm"},
        {"key": "no", "desc": "Go back", "goto": "node_description"},
    ]
    return text, options


def start_ultimate_wizard(caller):
    """
    Start the custom ultimate wizard.
    
    Args:
        caller: The character or account starting the wizard
    """
    _clear_wizard_data(caller)
    
    menu_kwargs = {
        "start_node": "node_start",
        "cmdset_mergetype": "Replace",
        "auto_quit": False,
        "auto_look": False,
        "node_input": True,
    }
    
    EvMenu(caller, MENU_NODES, **menu_kwargs)


MENU_NODES = {
    "node_start": node_start,
    "node_name": node_name,
    "node_attack_type": node_attack_type,
    "node_color": node_color,
    "node_description": node_description,
    "node_confirm": node_confirm,
}
