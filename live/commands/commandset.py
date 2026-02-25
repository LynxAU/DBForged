"""
Dedicated commandset for DB systems.
"""

from evennia.commands.cmdset import CmdSet

from commands.db_commands import (
    CmdAttack,
    CmdCharge,
    CmdCreateUltimate,
    CmdDBStats,
    CmdEquipTech,
    CmdEquipUltimate,
    CmdFlee,
    CmdHelpDB,
    CmdListTech,
    CmdLogout,
    CmdLogoTest,
    CmdPlayerProfile,
    CmdQuest,
    CmdQuests,
    CmdRacial,
    CmdRacials,
    CmdScan,
    CmdSense,
    CmdSuppress,
    CmdTech,
    CmdTrain,
    CmdTransform,
    CmdMap,
    CmdTechniqueUI,
    CmdForms,
    CmdLSSJ,
    CmdTalk,
    CmdSpawnTrainer,
    CmdUseUltimate,
    CmdGridMove,
    CmdTeleport,
    CmdNPCStress,
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
        self.add(CmdEquipUltimate())
        self.add(CmdCreateUltimate())
        self.add(CmdUseUltimate())
        self.add(CmdListTech())
        self.add(CmdScan())
        self.add(CmdSense())
        self.add(CmdSuppress())
        self.add(CmdTrain())
        self.add(CmdPlayerProfile())
        self.add(CmdMap())
        self.add(CmdTechniqueUI())
        self.add(CmdForms())
        self.add(CmdRacials())
        self.add(CmdRacial())
        self.add(CmdQuests())
        self.add(CmdQuest())
        self.add(CmdLSSJ())
        self.add(CmdTalk())
        self.add(CmdSpawnTrainer())
        self.add(CmdLogoTest())
        self.add(CmdLogout())
        self.add(CmdHelpDB())
        self.add(CmdGridMove())
        self.add(CmdTeleport())
        self.add(CmdNPCStress())
