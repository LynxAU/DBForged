"""
Social commands module.

Contains quest, guild, shop, talk, inventory, and other social/interaction commands.
"""

from __future__ import annotations

from commands.command import Command
from world.input_validation import (
    sanitize_name,
    sanitize_guild_name,
    sanitize_quest_id,
    validate_numeric,
    strip_evennia_markup,
)
from world.quests import (
    accept_quest,
    get_quest_definition,
    get_quest_status,
    get_quests_for_npc,
    mark_quest_turn_in_ready,
    turn_in_quest,
)
from world.guilds import (
    create_guild,
    get_guild,
    get_guild_by_name,
    get_player_guild,
    join_guild,
    leave_guild,
    invite_to_guild,
    kick_from_guild,
    promote_member,
    set_guild_motd,
    disband_guild,
    list_guilds,
    get_guild_members,
    GUILD_ROLE_LEADER,
    GUILD_ROLE_OFFICER,
    GUILD_ROLE_MEMBER,
    GUILD_CREATION_COST,
)


class CmdQuests(Command):
    """
    List your active quests.

    Usage:
      quests

    Shows all quests you've accepted and their status.
    """
    key = "quests"

    def func(self):
        caller = self.caller

        quest_ids = caller.db.active_quests or []

        if not quest_ids:
            caller.msg("You have no active quests.")
            return

        lines = ["=== Active Quests ==="]
        for qid in quest_ids:
            status = get_quest_status(caller, qid)
            definition = get_quest_definition(qid)

            if definition:
                lines.append(f"  {definition.get('name', qid)}")
                lines.append(f"    {definition.get('description', '')[:50]}...")
                if status.get("ready_to_turn_in"):
                    lines.append("    |g[READY TO TURN IN]|n")

        caller.msg("\n".join(lines))


class CmdQuest(Command):
    """
    Interact with a quest.

    Usage:
      quest accept <quest_id>
      quest turnin <quest_id>
      quest info <quest_id>

    Accept, turn in, or view details of a quest.
    """
    key = "quest"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: quest [accept|turnin|info] <quest_id>")
            return

        parts = self.args.strip().split(None, 1)
        if len(parts) < 2:
            caller.msg("Usage: quest [accept|turnin|info] <quest_id>")
            return

        action = parts[0].lower()
        quest_id_raw = parts[1].strip()
        
        # Sanitize quest ID
        quest_id = sanitize_quest_id(quest_id_raw)
        if not quest_id:
            caller.msg("Invalid quest ID.")
            return

        if action == "accept":
            result = accept_quest(caller, quest_id)
            if result.get("success"):
                caller.msg(f"Quest accepted: {result.get('quest_name')}")
            else:
                caller.msg(result.get("reason", "Failed to accept quest."))

        elif action == "turnin":
            result = turn_in_quest(caller, quest_id)
            if result.get("success"):
                caller.msg(f"Quest completed! Rewards: {result.get('rewards', '')}")
            else:
                caller.msg(result.get("reason", "Failed to turn in quest."))

        elif action == "info":
            definition = get_quest_definition(quest_id)
            if not definition:
                caller.msg(f"Quest '{quest_id}' not found.")
                return

            lines = [f"=== {definition.get('name', quest_id)} ==="]
            lines.append(definition.get("description", ""))
            lines.append(f"Rewards: {definition.get('rewards', 'None')}")

            caller.msg("\n".join(lines))

        else:
            caller.msg("Usage: quest [accept|turnin|info] <quest_id>")


class CmdTalk(Command):
    """
    Talk to an NPC.

    Usage:
      talk <npc>

    Initiate conversation with an NPC. They may offer quests,
    shop services, or other interactions.
    """
    key = "talk"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: talk <npc_name>")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            caller.msg(f"Couldn't find '{self.args.strip()}' here.")
            return

        if not target.db.is_npc:
            caller.msg("You can only talk to NPCs.")
            return

        npc_def = target.db.npc_definition
        if not npc_def:
            caller.msg(f"{target.key} has nothing to say.")
            return

        dialogue = npc_def.get("dialogue", "Hello there!")
        caller.msg(f"{target.key}: \"{dialogue}\"")

        # Check for available quests
        quests = get_quests_for_npc(target.key)
        if quests:
            caller.msg(f"{target.key} has quests available. Type 'quests' to view.")


class CmdShop(Command):
    """
    View a shop's inventory.

    Usage:
      shop [npc]

    Shows items available for purchase from an NPC shop.
    """
    key = "shop"

    def func(self):
        caller = self.caller

        if self.args:
            target = caller.search(self.args.strip(), location=caller.location)
            if not target:
                return
        else:
            target = None
            for obj in caller.location.contents:
                if obj != caller and getattr(obj.db, "is_npc", False) and obj.db.npc_definition:
                    shop_data = obj.db.npc_definition.get("shop")
                    if shop_data:
                        target = obj
                        break

        if not target:
            caller.msg("There's no shop here.")
            return

        shop_data = target.db.npc_definition.get("shop", {})
        items = shop_data.get("items", [])

        if not items:
            caller.msg(f"{target.key} has nothing for sale.")
            return

        lines = [f"=== {target.key}'s Shop ==="]
        for item in items:
            name = item.get("name", "Unknown")
            price = item.get("price", 0)
            lines.append(f"  {name}: {price} zeni")

        caller.msg("\n".join(lines))


class CmdBuy(Command):
    """
    Buy an item from a shop.

    Usage:
      buy <item>

    Purchase an item from the current shop.
    """
    key = "buy"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: buy <item_name>")
            return

        item_name = self.args.strip().lower()

        # Find shop NPC
        shop_npc = None
        for obj in caller.location.contents:
            if obj != caller and getattr(obj.db, "is_npc", False):
                shop_data = obj.db.npc_definition.get("shop") if obj.db.npc_definition else {}
                if shop_data.get("items"):
                    shop_npc = (obj, shop_data)
                    break

        if not shop_npc:
            caller.msg("There's no shop here.")
            return

        npc, shop_data = shop_npc
        items = shop_data.get("items", [])

        item = None
        for it in items:
            if it.get("name", "").lower() == item_name:
                item = it
                break

        if not item:
            caller.msg(f"'{item_name}' is not sold here.")
            return

        price = item.get("price", 0)
        zeni = caller.db.zeni or 0

        if zeni < price:
            caller.msg(f"You need {price} zeni. You have {zeni}.")
            return

        caller.db.zeni = zeni - price

        # Add item to inventory
        inventory = list(caller.db.inventory or [])
        inventory.append(item.get("name"))
        caller.db.inventory = inventory

        caller.msg(f"Bought {item.get('name')} for {price} zeni.")


class CmdSell(Command):
    """
    Sell an item to a shop.

    Usage:
      sell <item>

    Sell an item from your inventory to the current shop.
    """
    key = "sell"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: sell <item_name>")
            return

        item_name = self.args.strip().lower()
        inventory = caller.db.inventory or []

        item = None
        for it in inventory:
            if it.lower() == item_name:
                item = it
                break

        if not item:
            caller.msg(f"You don't have '{item_name}'.")
            return

        # Find shop for price
        sell_price = 10  # Default
        for obj in caller.location.contents:
            if getattr(obj.db, "is_npc", False):
                shop_data = obj.db.npc_definition.get("shop", {}) if obj.db.npc_definition else {}
                if shop_data.get("items"):
                    for it in shop_data.get("items", []):
                        if it.get("name", "").lower() == item_name.lower():
                            sell_price = it.get("price", 10) // 2
                            break

        caller.db.zeni = (caller.db.zeni or 0) + sell_price
        inventory.remove(item)
        caller.db.inventory = inventory

        caller.msg(f"Sold {item} for {sell_price} zeni.")


class CmdInventory(Command):
    """
    View your inventory.

    Usage:
      inventory
      inv

    Shows all items you're carrying.
    """
    key = "inventory"
    aliases = ["inv", "i"]

    def func(self):
        caller = self.caller

        inventory = caller.db.inventory or []

        if not inventory:
            caller.msg("Your inventory is empty.")
            return

        lines = ["=== Inventory ==="]
        for item in inventory:
            lines.append(f"  - {item}")

        caller.msg("\n".join(lines))


class CmdGuild(Command):
    """
    Manage guild operations.

    Usage:
      guild create <name>
      guild info [name]
      guild invite <player>
      guild kick <player>
      guild leave
      guild motd <message>
      guild list

    Various guild management commands.
    """
    key = "guild"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: guild [create|info|invite|kick|leave|motd|list]")
            return

        parts = self.args.strip().split(None, 1)
        action = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if action == "create":
            if not arg:
                caller.msg("Usage: guild create <name>")
                return

            # Validate guild name
            guild_name = sanitize_guild_name(arg)
            if not guild_name:
                caller.msg("Invalid guild name. Use only letters, numbers, spaces, hyphens, and underscores.")
                return

            cost = GUILD_CREATION_COST
            zeni = caller.db.zeni or 0
            if zeni < cost:
                caller.msg(f"Guild creation costs {cost} zeni.")
                return

            caller.db.zeni = zeni - cost
            result = create_guild(caller, guild_name)

            if result.get("success"):
                caller.msg(f"Guild '{guild_name}' created!")
            else:
                caller.msg(result.get("reason", "Failed to create guild."))

        elif action == "info":
            if arg:
                guild = get_guild_by_name(arg)
            else:
                guild = get_player_guild(caller.id)

            if not guild:
                caller.msg("Guild not found.")
                return

            lines = [f"=== {guild.name} ==="]
            lines.append(f"MOTD: {guild.db.motd or 'None'}")
            lines.append(f"Leader: {guild.get_leader_name()}")

            members = guild.db.members or {}
            lines.append(f"Members: {len(members)}/{guild.max_members}")

            caller.msg("\n".join(lines))

        elif action == "invite":
            if not arg:
                caller.msg("Usage: guild invite <player>")
                return

            guild = get_player_guild(caller.id)
            if not guild:
                caller.msg("You're not in a guild.")
                return

            # Check permission
            member = guild.db.members.get(str(caller.id), {})
            role = member.get("role", 0)
            if role < GUILD_ROLE_OFFICER:
                caller.msg("Only officers can invite.")
                return

            target = caller.search(arg, location=caller.location)
            if not target:
                caller.msg(f"Can't find '{arg}'.")
                return

            result = invite_to_guild(guild, target.id, target.key)
            caller.msg(result.get("reason", result.get("success", False) and "Invited." or "Failed."))

        elif action == "kick":
            if not arg:
                caller.msg("Usage: guild kick <player>")
                return

            guild = get_player_guild(caller.id)
            if not guild:
                caller.msg("You're not in a guild.")
                return

            member = guild.db.members.get(str(caller.id), {})
            if member.get("role") != GUILD_ROLE_LEADER:
                caller.msg("Only the guild leader can kick members.")
                return

            result = kick_from_guild(guild, arg)
            caller.msg(result.get("reason", result.get("success", False) and "Kicked." or "Failed."))

        elif action == "leave":
            guild = get_player_guild(caller.id)
            if not guild:
                caller.msg("You're not in a guild.")
                return

            result = leave_guild(guild, caller.id, caller.key)
            caller.msg(result.get("reason", result.get("success", False) and "Left guild." or "Failed."))

        elif action == "motd":
            guild = get_player_guild(caller.id)
            if not guild:
                caller.msg("You're not in a guild.")
                return

            member = guild.db.members.get(str(caller.id), {})
            if member.get("role") < GUILD_ROLE_OFFICER:
                caller.msg("Only officers can set MOTD.")
                return

            # Sanitize MOTD - strip markup
            motd = strip_evennia_markup(arg)
            if len(motd) > 200:
                motd = motd[:200]
            
            result = set_guild_motd(guild, motd)
            caller.msg("MOTD updated." if result.get("success") else "Failed.")

        elif action == "list":
            guilds = list_guilds()
            if not guilds:
                caller.msg("No guilds exist.")
                return

            lines = ["=== Guilds ==="]
            for g in guilds:
                members = g.db.members or {}
                lines.append(f"  {g.name}: {len(members)} members")

            caller.msg("\n".join(lines))

        else:
            caller.msg("Usage: guild [create|info|invite|kick|leave|motd|list]")


# Export all social commands
__all__ = [
    "CmdQuests",
    "CmdQuest",
    "CmdTalk",
    "CmdShop",
    "CmdBuy",
    "CmdSell",
    "CmdInventory",
    "CmdGuild",
]
