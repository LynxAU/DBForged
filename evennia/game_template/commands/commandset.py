"""
Dedicated commandset for DB systems.
"""

from evennia.commands.cmdset import CmdSet

from commands.db_commands import (
    CmdAttack,
    CmdCharge,
    CmdDBStats,
    CmdEquipTech,
    CmdFlee,
    CmdHelpDB,
    CmdListTech,
    CmdLogoTest,
    CmdPlayerProfile,
    CmdScan,
    CmdSense,
    CmdSuppress,
    CmdTeleport,
    CmdTech,
    CmdTrain,
    CmdTransform,
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
        self.add(CmdScan())
        self.add(CmdSense())
        self.add(CmdSuppress())
        self.add(CmdTrain())
        self.add(CmdPlayerProfile())
        self.add(CmdTeleport())
        self.add(CmdLogoTest())
        self.add(CmdHelpDB())
