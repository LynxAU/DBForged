"""
Dedicated commandset for DB systems.
"""

from evennia.commands.cmdset import CmdSet

# Import from new modular command files
from commands.combat_cmds import (
    CmdAttack,
    CmdCharge,
    CmdCounter,
    CmdFlee,
    CmdGuard,
)
from commands.character_cmds import (
    CmdDBStats,
    CmdEquipTech,
    CmdFly,
    CmdListTech,
    CmdPlayerProfile,
    CmdScan,
    CmdSense,
    CmdSuppress,
    CmdTech,
    CmdTransform,
)
from commands.social_cmds import (
    CmdGuild,
)

# Legacy commands still in db_commands
from commands.db_commands import (
    CmdCombatHUD,
    CmdTrain,
    CmdLogoTest,
    CmdHelpDB,
    CmdTeleportPlayer,
)


class DBSystemCmdSet(CmdSet):
    key = "DBSystemCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdDBStats())
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdCharge())
        self.add(CmdTransform())
        self.add(CmdTech())
        self.add(CmdEquipTech())
        self.add(CmdListTech())
        self.add(CmdCombatHUD())
        self.add(CmdGuard())
        self.add(CmdCounter())
        self.add(CmdScan())
        self.add(CmdSense())
        self.add(CmdSuppress())
        self.add(CmdTrain())
        self.add(CmdPlayerProfile())
        self.add(CmdTeleportPlayer())
        self.add(CmdFly())
        self.add(CmdLogoTest())
        self.add(CmdHelpDB())
        self.add(CmdGuild())
