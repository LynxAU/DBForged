r"""
Evennia settings file.
"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game
SERVERNAME = "DBForged"
DBFORGED_VERSION = "0.1"

# Telnet port
TELNET_PORT = 5555

# Use game-local cmdsets so DBForged commands mount correctly.
CMDSET_UNLOGGEDIN = "commands.default_cmdsets.UnloggedinCmdSet"
CMDSET_SESSION = "commands.default_cmdsets.SessionCmdSet"
CMDSET_CHARACTER = "commands.default_cmdsets.CharacterCmdSet"
CMDSET_ACCOUNT = "commands.default_cmdsets.AccountCmdSet"

# Testing-friendly default during development
AUTO_PUPPET_ON_LOGIN = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 0

# Global scripts for game systems
GLOBAL_SCRIPTS = {
    "experience": {
        "typeclass": "typeclasses.scripts.GlobalScript",
        "interval": 0,
        "persistent": True,
    },
    "economy": {
        "typeclass": "typeclasses.scripts.GlobalScript", 
        "interval": 0,
        "persistent": True,
    },
    "combat": {
        "typeclass": "typeclasses.scripts.GlobalScript",
        "interval": 0,
        "persistent": True,
    },
    "tournament": {
        "typeclass": "typeclasses.scripts.GlobalScript",
        "interval": 0,
        "persistent": True,
    },
    "dragonballs": {
        "typeclass": "typeclasses.scripts.GlobalScript",
        "interval": 0,
        "persistent": True,
    },
    "timechamber": {
        "typeclass": "typeclasses.scripts.GlobalScript",
        "interval": 0,
        "persistent": True,
    },
}


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
