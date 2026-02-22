r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = {servername}
DBFORGED_VERSION = "0.1"

# Use game-local cmdsets so DBForged commands mount correctly.
CMDSET_UNLOGGEDIN = "commands.default_cmdsets.UnloggedinCmdSet"
CMDSET_SESSION = "commands.default_cmdsets.SessionCmdSet"
CMDSET_CHARACTER = "commands.default_cmdsets.CharacterCmdSet"
CMDSET_ACCOUNT = "commands.default_cmdsets.AccountCmdSet"

# Testing-friendly default during development: don't auto-puppet after login.
AUTO_PUPPET_ON_LOGIN = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 0

# Keep combat loop available across reloads/restarts.
GLOBAL_SCRIPTS = {{
    "db_combat": {{
        "typeclass": "world.combat.CombatHandler",
        "interval": 1,
        "persistent": True,
        "start_delay": True,
    }}
}}


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
