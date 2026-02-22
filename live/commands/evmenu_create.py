"""
DBForged EvMenu-based Character Creation

This module provides an Evennia EvMenu-based character creation system
that properly handles all text input.
"""

from evennia.utils.evmenu import EvMenu
from typeclasses.characters import RACE_OPTIONS, SEX_OPTIONS, RACE_DISPLAY_NAMES
from world.color_utils import colorize

# Character creation data stored on the account
def _get_create_data(account, session):
    """Get or initialize character creation data"""
    state = account._db_menu_state(session=session)
    if "create_data" not in state:
        state["create_data"] = {}
    return state["create_data"]

def _save_create_data(account, session, key, value):
    """Save a character creation data field"""
    state = account._db_menu_state(session=session)
    if "create_data" not in state:
        state["create_data"] = {}
    state["create_data"][key] = value

def _clear_create_data(account, session):
    """Clear character creation data"""
    state = account._db_menu_state(session=session)
    state.pop("create_data", None)
    state.pop("create_step", None)

def _get_step(account, session):
    """Get current creation step"""
    state = account._db_menu_state(session=session)
    return state.get("create_step", 0)

def _set_step(account, session, step):
    """Set current creation step"""
    state = account._db_menu_state(session=session)
    state["create_step"] = step

# Menu nodes
def node_start(caller, session=None):
    """Start character creation"""
    text = """
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Welcome to the Character Creation Wizard!                                   
|                                                                             
| This wizard will guide you through creating your new character.            
|                                                                             
| Press |cC|n to cancel and return to the main menu at any time.               
|                                                                             
| Press |cB|n to go back to the previous step.                                  
|                                                                             
+-----------------------------------------------------------------------------+
"""
    options = [
        {"key": "continue", "desc": "Begin character creation", "goto": "node_name"}
    ]
    return text, options

def node_name(caller, session=None, input=None):
    """Character name input node"""
    data = _get_create_data(caller, session)
    
    if input:
        # Validate the name
        name = input.strip()
        if not name:
            caller.msg("|rCharacter name cannot be blank.|n")
            return "node_name", {}
        if len(name) < 3:
            caller.msg("|rCharacter name must be at least 3 characters.|n")
            return "node_name", {}
        if len(name) > 24:
            caller.msg("|rCharacter name must be 24 characters or less.|n")
            return "node_name", {}
        
        # Save name and move to next step
        _save_create_data(caller, session, "name", name)
        _set_step(caller, session, 1)
        return "node_race", {}
    
    # Show the prompt
    current = data.get("name", "-")
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 1/7 - Name                                                           
|                                                                             
| Enter your character name:                                                  
| Current: {current:<10}                                                      
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_race(caller, session=None, input=None):
    """Race selection node"""
    data = _get_create_data(caller, session)
    
    # Build race options text
    race_list = []
    for i, race in enumerate(RACE_OPTIONS, 1):
        display = RACE_DISPLAY_NAMES.get(race, race.replace("_", " ").title())
        race_list.append(f"  |c{i}|n - {display}")
    race_text = "\n".join(race_list)
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 0)
            return "node_name", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            # Return to main menu
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate race selection
        try:
            choice = int(input.strip())
            if 1 <= choice <= len(RACE_OPTIONS):
                race = RACE_OPTIONS[choice - 1]
                _save_create_data(caller, session, "race", race)
                _set_step(caller, session, 2)
                return "node_sex", {}
        except ValueError:
            pass
        caller.msg("|rPlease enter a valid number.|n")
    
    current = data.get("race", "-")
    current_display = RACE_DISPLAY_NAMES.get(current, current.replace("_", " ").title()) if current != "-" else "-"
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 2/7 - Race                                                           
|                                                                             
| Choose your race:                                                          
|                                                                             
{race_text}
|                                                                             
| Current: {current_display:<20}                                              
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_sex(caller, session=None, input=None):
    """Sex selection node"""
    data = _get_create_data(caller, session)
    
    sex_list = []
    for i, sex in enumerate(SEX_OPTIONS, 1):
        display = sex.replace("_", " ").title()
        sex_list.append(f"  |c{i}|n - {display}")
    sex_text = "\n".join(sex_list)
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 1)
            return "node_race", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate sex selection
        try:
            choice = int(input.strip())
            if 1 <= choice <= len(SEX_OPTIONS):
                sex = SEX_OPTIONS[choice - 1]
                _save_create_data(caller, session, "sex", sex)
                _set_step(caller, session, 3)
                return "node_hair_style", {}
        except ValueError:
            pass
        caller.msg("|rPlease enter a valid number.|n")
    
    current = data.get("sex", "-")
    current_display = current.replace("_", " ").title() if current != "-" else "-"
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 3/7 - Sex                                                             
|                                                                             
| Choose your sex:                                                           
|                                                                             
{sex_text}
|                                                                             
| Current: {current_display:<20}                                              
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_hair_style(caller, session=None, input=None):
    """Hair style selection node"""
    data = _get_create_data(caller, session)
    
    hair_styles = ["short", "long", "mohawk", "bald", "curly", "braided"]
    hair_list = []
    for i, style in enumerate(hair_styles, 1):
        display = style.replace("_", " ").title()
        hair_list.append(f"  |c{i}|n - {display}")
    hair_text = "\n".join(hair_list)
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 2)
            return "node_sex", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate hair style selection
        try:
            choice = int(input.strip())
            if 1 <= choice <= len(hair_styles):
                style = hair_styles[choice - 1]
                _save_create_data(caller, session, "hair_style", style)
                _set_step(caller, session, 4)
                return "node_hair_color", {}
        except ValueError:
            pass
        caller.msg("|rPlease enter a valid number.|n")
    
    current = data.get("hair_style", "-")
    current_display = current.replace("_", " ").title() if current != "-" else "-"
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 4/7 - Hair Style                                                     
|                                                                             
| Choose your hair style:                                                    
|                                                                             
{hair_text}
|                                                                             
| Current: {current_display:<20}                                              
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_hair_color(caller, session=None, input=None):
    """Hair color selection node"""
    data = _get_create_data(caller, session)
    
    hair_colors = ["black", "brown", "blonde", "red", "white", "blue", "green", "purple"]
    color_list = []
    for i, color in enumerate(hair_colors, 1):
        display = color.replace("_", " ").title()
        color_list.append(f"  |c{i}|n - {display}")
    color_text = "\n".join(color_list)
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 3)
            return "node_hair_style", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate hair color selection
        try:
            choice = int(input.strip())
            if 1 <= choice <= len(hair_colors):
                color = hair_colors[choice - 1]
                _save_create_data(caller, session, "hair_color", color)
                _set_step(caller, session, 5)
                return "node_eye_color", {}
        except ValueError:
            pass
        caller.msg("|rPlease enter a valid number.|n")
    
    current = data.get("hair_color", "-")
    current_display = current.replace("_", " ").title() if current != "-" else "-"
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 5/7 - Hair Color                                                     
|                                                                             
| Choose your hair color:                                                   
|                                                                             
{color_text}
|                                                                             
| Current: {current_display:<20}                                              
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_eye_color(caller, session=None, input=None):
    """Eye color selection node"""
    data = _get_create_data(caller, session)
    
    eye_colors = ["brown", "blue", "green", "hazel", "gray", "black", "red", "purple"]
    color_list = []
    for i, color in enumerate(eye_colors, 1):
        display = color.replace("_", " ").title()
        color_list.append(f"  |c{i}|n - {display}")
    color_text = "\n".join(color_list)
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 4)
            return "node_hair_color", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate eye color selection
        try:
            choice = int(input.strip())
            if 1 <= choice <= len(eye_colors):
                color = eye_colors[choice - 1]
                _save_create_data(caller, session, "eye_color", color)
                _set_step(caller, session, 6)
                return "node_aura_color", {}
        except ValueError:
            pass
        caller.msg("|rPlease enter a valid number.|n")
    
    current = data.get("eye_color", "-")
    current_display = current.replace("_", " ").title() if current != "-" else "-"
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 6/7 - Eye Color                                                      
|                                                                             
| Choose your eye color:                                                     
|                                                                             
{color_text}
|                                                                             
| Current: {current_display:<20}                                              
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_aura_color(caller, session=None, input=None):
    """Aura color selection node"""
    data = _get_create_data(caller, session)
    
    aura_colors = ["none", "red", "blue", "green", "white", "black", "gold", "silver", "purple"]
    color_list = []
    for i, color in enumerate(aura_colors, 1):
        display = color.replace("_", " ").title()
        color_list.append(f"  |c{i}|n - {display}")
    color_text = "\n".join(color_list)
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 5)
            return "node_eye_color", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate aura color selection
        try:
            choice = int(input.strip())
            if 1 <= choice <= len(aura_colors):
                color = aura_colors[choice - 1]
                _save_create_data(caller, session, "aura_color", color)
                _set_step(caller, session, 7)
                return "node_review", {}
        except ValueError:
            pass
        caller.msg("|rPlease enter a valid number.|n")
    
    current = data.get("aura_color", "-")
    current_display = current.replace("_", " ").title() if current != "-" else "-"
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Step 7/7 - Aura Color                                                     
|                                                                             
| Choose your aura color (affects magical presence):                         
|                                                                             
{color_text}
|                                                                             
| Current: {current_display:<20}                                              
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def node_review(caller, session=None, input=None):
    """Review and confirm character"""
    data = _get_create_data(caller, session)
    
    name = data.get("name", "-")
    race = data.get("race", "-")
    race_display = RACE_DISPLAY_NAMES.get(race, race.replace("_", " ").title()) if race != "-" else "-"
    sex = data.get("sex", "-").replace("_", " ").title() if data.get("sex") != "-" else "-"
    hair_style = data.get("hair_style", "-").replace("_", " ").title() if data.get("hair_style") != "-" else "-"
    hair_color = colorize(data.get("hair_color"), data.get("hair_color", "-").replace("_", " ").title()) if data.get("hair_color") != "-" else "-"
    eye_color = colorize(data.get("eye_color"), data.get("eye_color", "-").replace("_", " ").title()) if data.get("eye_color") != "-" else "-"
    aura_color = colorize(data.get("aura_color"), data.get("aura_color", "-").replace("_", " ").title()) if data.get("aura_color") != "-" else "-"
    
    if input:
        # Handle special commands
        if input.lower() in ["b", "back"]:
            _set_step(caller, session, 6)
            return "node_aura_color", {}
        if input.lower() == "c":
            _clear_create_data(caller, session)
            caller._db_menu_reset(session=session)
            caller._db_menu_send(session=session)
            return None
        
        # Validate choice
        if input.strip() == "1":
            # Create the character
            return create_character(caller, session, data)
        elif input.strip() == "2":
            # Go back to race selection
            _set_step(caller, session, 1)
            return "node_race", {}
        else:
            caller.msg("|rPlease enter 1 or 2.|n")
    
    text = f"""
|w+-----------------------------------------------------------------------------+
|                             CHARACTER CREATION                             
|+-----------------------------------------------------------------------------+
|                                                                             
| Review Your Character                                                      
|                                                                             
| Name:     {name:<20}                                            
| Race:     {race_display:<20}                                            
| Sex:      {sex:<20}                                            
| Hair:     {hair_style} {hair_color:<15}                              
| Eyes:     {eye_color:<20}                                            
| Aura:     {aura_color:<20}                                            
|                                                                             
|                                                                             
+-----------------------------------------------------------------------------+
|                                                                             
| |c1|n - Create this character                                              
| |c2|n - Go back to change race                                             
|                                                                             
| B = Back   C = Cancel                                                      
+-----------------------------------------------------------------------------+
"""
    options = []
    return text, options

def create_character(caller, session, data):
    """Create the character with the gathered data"""
    name = data.get("name")
    race = data.get("race")
    sex = data.get("sex")
    hair_style = data.get("hair_style")
    hair_color = data.get("hair_color")
    eye_color = data.get("eye_color")
    aura_color = data.get("aura_color")
    
    # Debug: print what we're trying to create
    caller.msg(f"[DEBUG] Creating character: {name} for account {caller.key}", session=session)
    
    # Build description
    desc = f"A {race.replace('_', ' ')} {sex} with {hair_style.replace('_', ' ')} {hair_color} hair and {eye_color} eyes."
    
    # Create character
    new_character, errors = caller.create_character(
        key=name,
        description=desc,
        ip=(session.address if session else "")
    )
    
    caller.msg(f"[DEBUG] create_character returned: char={new_character}, errors={errors}", session=session)
    
    if errors:
        caller.msg(f"|r{errors}|n", session=session)
        _clear_create_data(caller, session)
        caller._db_menu_reset(session=session)
        caller._db_menu_send(session=session)
        return None
    
    if not new_character:
        caller.msg("|rCharacter creation failed.|n", session=session)
        _clear_create_data(caller, session)
        caller._db_menu_reset(session=session)
        caller._db_menu_send(session=session)
        return None
    
    # Debug: check if character is linked to account
    caller.msg(f"[DEBUG] Character dbobj: {new_character}", session=session)
    caller.msg(f"[DEBUG] Character account: {new_character.account}", session=session)
    caller.msg(f"[DEBUG] Account characters: {list(caller.characters)}", session=session)
    
    # Set character attributes
    for key in ("race", "sex", "hair_style", "hair_color", "eye_color", "aura_color"):
        setattr(new_character.db, key, data[key])
    
    # Set skin color based on race (simplified)
    new_character.db.skin_color = "medium"
    new_character.db.chargen_complete = True
    new_character.db.chargen_step_index = 0
    
    caller.msg(f"[DEBUG] Set chargen_complete=True on {new_character.key}", session=session)
    
    if hasattr(new_character, "_refresh_sprite_id"):
        new_character._refresh_sprite_id()
    
    # Clear create data and show success
    _clear_create_data(caller, session)
    
    caller.msg(f"|gCharacter created:|n |w{new_character.key}|n", session=session)
    
    # Return to character selection
    state = caller._db_menu_state(session=session)
    state["mode"] = "enter_select"
    caller._db_menu_render_charlist(session=session, for_delete=False)
    
    # Return None to end the EvMenu
    return None


def start_character_creation(caller, session=None):
    """
    Start the EvMenu-based character creation.
    Call this from the menu command.
    """
    # Clear any existing create data
    _clear_create_data(caller, session)
    
    # Remove any existing EvMenu cmdsets first
    from evennia.utils.evmenu import EvMenuCmdSet
    try:
        caller.cmdset.remove(EvMenuCmdSet)
    except Exception:
        pass
    
    # Set a flag to indicate EvMenu character creation is active
    # This helps other commands detect that EvMenu is running
    if not hasattr(caller.ndb, 'evmenu_create_active'):
        caller.ndb.evmenu_create_active = True
    else:
        caller.ndb.evmenu_create_active = True
    
    # Start EvMenu with higher priority to override account commands
    EvMenu(
        caller,
        {
            "node_start": node_start,
            "node_name": node_name,
            "node_race": node_race,
            "node_sex": node_sex,
            "node_hair_style": node_hair_style,
            "node_hair_color": node_hair_color,
            "node_eye_color": node_eye_color,
            "node_aura_color": node_aura_color,
            "node_review": node_review,
        },
        startnode="node_start",
        session=session,
        auto_quit=False,
        auto_look=False,
        auto_help=False,
        cmdset_priority=10,  # Higher priority to override account cmdset
        cmdset_mergetype="Replace",
    )
