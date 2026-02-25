"""
Dedicated commandset for DB systems.
"""

from evennia.commands.cmdset import CmdSet

from commands.db_commands import (
    CmdAttack,
    CmdBoss,
    CmdCharge,
    CmdClearStatus,
    CmdCreateUltimate,
    CmdDBStats,
    CmdDragonBall,
    CmdDrop,
    CmdDungeon,
    CmdEquip,
    CmdFlightStatus,
    CmdFly,
    CmdFriend,
    CmdLand,
    CmdMentor,
    CmdEquipTech,
    CmdEquipUltimate,
    CmdFaction,
    CmdFlurry,
    CmdFuse,
    CmdFlee,
    CmdHelpDB,
    CmdHTC,
    CmdInstantTransmission,
    CmdInventory,
    CmdListTech,
    CmdLogoTest,
    CmdLogout,
    CmdMastery,
    CmdParty,
    CmdPlanetCracker,
    CmdPlayerProfile,
    CmdPush,
    CmdQuest,
    CmdQuests,
    CmdRacial,
    CmdRacials,
    CmdScan,
    CmdSense,
    CmdSpiritBomb,
    CmdStatus,
    CmdStatusInfo,
    CmdSuppress,
    CmdSummonShenron,
    CmdTech,
    CmdTeleport,
    CmdTimeskip,
    CmdTrainWith,
    CmdTrain,
    CmdTransform,
    CmdMap,
    CmdTechniqueUI,
    CmdForms,
    CmdLSSJ,
    CmdTalk,
    CmdSpawnTrainer,
    CmdUnequip,
    CmdUseUltimate,
    CmdWish,
    CmdUse,
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
        self.add(CmdMastery())
        self.add(CmdPush())
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
        self.add(CmdTrainWith())
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
        self.add(CmdSpiritBomb())
        self.add(CmdFlurry())
        self.add(CmdFuse())
        self.add(CmdTimeskip())
        self.add(CmdTeleport())
        self.add(CmdInstantTransmission())
        self.add(CmdDragonBall())
        self.add(CmdSummonShenron())
        self.add(CmdWish())
        self.add(CmdPlanetCracker())
        # Status Effects Commands
        self.add(CmdStatus())
        self.add(CmdClearStatus())
        self.add(CmdStatusInfo())
        # Inventory Commands
        self.add(CmdInventory())
        self.add(CmdUse())
        self.add(CmdEquip())
        self.add(CmdUnequip())
        self.add(CmdDrop())
        self.add(CmdParty())
        self.add(CmdBoss())
        self.add(CmdFaction())
        self.add(CmdHTC())
        self.add(CmdDungeon())
        self.add(CmdFly())
        self.add(CmdLand())
        self.add(CmdFlightStatus())
        self.add(CmdMentor())
        self.add(CmdFriend())
