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

import os

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Keep the repo default live-safe, and let
# local/dev instances override via env var or secret_settings.py.
SERVERNAME = os.environ.get("DBFORGED_SERVERNAME", "live")
DBFORGED_VERSION = "0.1"
DBFORGED_EMIT_CLIENT_EVENTS = False

# Port configuration - use 5143+ range for testing (different from Codex 5143-5149)
TELNET_PORTS = [5153]
WEBSERVER_PORTS = [(5154, 5158)]
WEBSOCKET_CLIENT_PORT = 5155
SSL_PORTS = [5156]
SSH_PORTS = [5157]
AMP_PORT = 5159

# Use game-local cmdsets so DBForged commands mount correctly.
CMDSET_UNLOGGEDIN = "commands.default_cmdsets.UnloggedinCmdSet"
CMDSET_SESSION = "commands.default_cmdsets.SessionCmdSet"
CMDSET_CHARACTER = "commands.default_cmdsets.CharacterCmdSet"
CMDSET_ACCOUNT = "commands.default_cmdsets.AccountCmdSet"

# Post-login always lands in the DBForged account menu until the player chooses Enter Game.
AUTO_PUPPET_ON_LOGIN = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# Keep combat loop available across reloads/restarts.
GLOBAL_SCRIPTS = {
    "db_combat": {
        "typeclass": "world.combat.CombatHandler",
        "interval": 1,
        "persistent": True,
        "start_delay": True,
    }
}

# Removed dynamic port section
######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
