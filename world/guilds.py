"""
Guild system for DBForged.

This module implements:
- Guild creation
- Guild membership management
- Guild chat
- Database-backed persistence using Evennia's Attribute system
"""

from __future__ import annotations

import time
from typing import Any, Optional

from django.conf import settings
from evennia import DefaultObject
from evennia.utils.create import create_object
from evennia.utils.search import search_object


# Guild roles
GUILD_ROLE_LEADER = "leader"
GUILD_ROLE_OFFICER = "officer"
GUILD_ROLE_MEMBER = "member"

# Guild settings
MAX_GUILD_NAME_LENGTH = 30
MAX_GUILD_MEMBERS = 50
GUILD_CREATION_COST = 5000


class Guild(DefaultObject):
    """
    A guild is a player organization with ranks and member management.
    
    Guild ranks:
    - Leader: Can manage all aspects of the guild
    - Officer: Can invite/kick members
    - Member: Standard member
    
    Guilds have:
    - name: The guild's display name
    - description: Guild description/motd
    - leader: Account DBREF of the guild leader
    - members: Dict of member account DBREFs to member data
    - rank_perms: Dictionary of rank permissions
    - created_at: Timestamp of creation
    - zeni: Guild bank balance
    """

    def at_object_creation(self):
        """Initialize guild attributes on creation."""
        super().at_object_creation()
        # Core guild data
        self.db.guild_name = ""
        self.db.guild_description = ""
        self.db.leader = None  # Account dbref
        self.db.members = {}  # Dict: account_id -> {name, role, joined}
        self.db.motd = ""  # Message of the day
        self.db.created_at = None
        self.db.zeni = 0  # Guild bank
        self.db.invitations = []  # Pending invitations

    def add_member(self, account, name: str, role: str = GUILD_ROLE_MEMBER) -> bool:
        """Add an account to the guild."""
        account_id = str(account.id)
        members = self.db.members or {}
        
        if account_id not in members:
            members[account_id] = {
                "name": name,
                "role": role,
                "joined": time.time(),
            }
            self.db.members = members
            # Set guild info on the character
            self._update_character_guild(account)
            return True
        return False
    
    def remove_member(self, account) -> bool:
        """Remove an account from the guild."""
        account_id = str(account.id)
        members = dict(self.db.members or {})
        
        if account_id in members:
            del members[account_id]
            self.db.members = members
            
            # Clear guild info from character
            self._clear_character_guild(account)
            return True
        return False
    
    def get_member(self, account_id: str) -> Optional[dict]:
        """Get member data by account ID."""
        members = self.db.members or {}
        return members.get(account_id)
    
    def get_all_members(self) -> dict:
        """Get all members as a dict."""
        return dict(self.db.members or {})
    
    def is_leader(self, account) -> bool:
        """Check if account is the guild leader."""
        return self.db.leader == str(account.id)
    
    def is_officer(self, account) -> bool:
        """Check if account is an officer or leader."""
        account_id = str(account.id)
        if self.is_leader(account):
            return True
        member = self.get_member(account_id)
        return member and member.get("role") in [GUILD_ROLE_LEADER, GUILD_ROLE_OFFICER]
    
    def is_member(self, account) -> bool:
        """Check if account is a guild member."""
        account_id = str(account.id)
        return self.is_leader(account) or account_id in (self.db.members or {})
    
    def set_member_role(self, account_id: str, role: str) -> bool:
        """Set a member's role."""
        members = dict(self.db.members or {})
        if account_id in members:
            members[account_id]["role"] = role
            self.db.members = members
            return True
        return False
    
    def add_zeni(self, amount: int) -> int:
        """Add zeni to guild bank. Returns new balance."""
        current = self.db.zeni or 0
        self.db.zeni = current + amount
        return self.db.zeni
    
    def remove_zeni(self, amount: int) -> bool:
        """Remove zeni from guild bank. Returns success."""
        current = self.db.zeni or 0
        if current >= amount:
            self.db.zeni = current - amount
            return True
        return False
    
    def get_zeni(self) -> int:
        """Get guild bank balance."""
        return self.db.zeni or 0
    
    def set_motd(self, motd: str):
        """Set the message of the day."""
        self.db.motd = motd
    
    def get_motd(self) -> str:
        """Get the message of the day."""
        return self.db.motd or ""
    
    def add_invitation(self, account_id: str):
        """Add a pending invitation."""
        invitations = list(self.db.invitations or [])
        if account_id not in invitations:
            invitations.append(account_id)
            self.db.invitations = invitations
    
    def remove_invitation(self, account_id: str):
        """Remove a pending invitation."""
        invitations = list(self.db.invitations or [])
        if account_id in invitations:
            invitations.remove(account_id)
            self.db.invitations = invitations
    
    def has_invitation(self, account_id: str) -> bool:
        """Check if account has pending invitation."""
        return account_id in (self.db.invitations or [])
    
    def get_member_count(self) -> int:
        """Get total number of members."""
        return len(self.db.members or {})
    
    def get_online_members(self) -> list:
        """Get list of currently online members."""
        from evennia.objects.models import ObjectDB
        online = []
        for member_id in (self.db.members or {}).keys():
            try:
                account = ObjectDB.objects.get(id=int(member_id))
                if account and hasattr(account, 'is_connected') and account.is_connected():
                    online.append(account)
            except (ValueError, ObjectDB.DoesNotExist):
                pass
        return online
    
    def _update_character_guild(self, account):
        """Update character with guild info."""
        if account.puppet:
            char = account.puppet
            char.db.guild = self.db.guild_name
            char.db.guild_rank = self._get_rank_name(account)
    
    def _clear_character_guild(self, account):
        """Clear guild info from character."""
        if account.puppet:
            char = account.puppet
            char.db.guild = None
            char.db.guild_rank = None
    
    def _get_rank_name(self, account):
        """Get the rank name for an account."""
        if self.is_leader(account):
            return "Leader"
        account_id = str(account.id)
        member = self.get_member(account_id)
        if member:
            role = member.get("role", GUILD_ROLE_MEMBER)
            if role == GUILD_ROLE_OFFICER:
                return "Officer"
            elif role == GUILD_ROLE_MEMBER:
                return "Member"
        return None
    
    def to_dict(self) -> dict:
        """Convert guild to dictionary for API responses."""
        members_list = []
        for member_id, data in (self.db.members or {}).items():
            members_list.append({
                "id": member_id,
                "name": data.get("name", "Unknown"),
                "role": data.get("role", GUILD_ROLE_MEMBER),
                "joined": data.get("joined", 0),
            })
        
        return {
            "id": str(self.id),
            "name": self.db.guild_name,
            "description": self.db.guild_description,
            "leader": self.db.leader,
            "leader_name": self._get_leader_name(),
            "members": members_list,
            "member_count": len(members_list),
            "motd": self.db.motd or "",
            "zeni": self.db.zeni or 0,
            "created": self.db.created_at,
        }
    
    def _get_leader_name(self) -> str:
        """Get the leader's name."""
        from evennia.objects.models import ObjectDB
        from django.core.exceptions import ObjectDoesNotExist
        
        leader_id = self.db.leader
        if leader_id:
            try:
                account = ObjectDB.objects.get(id=int(leader_id))
                if account:
                    return account.key
            except (ValueError, ObjectDoesNotExist):
                pass
        return "Unknown"


#-------------------------------------------------------------------------
# Factory Functions (Database-backed)
#-------------------------------------------------------------------------

def create_guild(name: str, leader_id: str, leader_name: str) -> dict:
    """Create a new guild."""
    # Check if guild name already exists
    existing = search_object(key=f"guild:{name.lower()}", typeclass="world.guilds.Guild")
    if existing:
        return {"success": False, "reason": "Guild name already exists"}
    
    # Create the guild object
    guild = create_object(
        "world.guilds.Guild",
        key=f"guild:{name.lower()}",
        location=None,
        home=None,
    )
    
    # Initialize guild data
    guild.db.guild_name = name
    guild.db.guild_description = ""
    guild.db.leader = leader_id
    guild.db.members = {
        leader_id: {
            "name": leader_name,
            "role": GUILD_ROLE_LEADER,
            "joined": time.time(),
        }
    }
    guild.db.motd = "Welcome to the guild!"
    guild.db.zeni = 0
    guild.db.created_at = time.time()
    guild.db.invitations = []
    
    return {"success": True, "guild": guild.to_dict()}


def get_guild(guild_id: str) -> Optional[Guild]:
    """Get guild by ID."""
    try:
        from evennia.objects.models import ObjectDB
        obj = ObjectDB.objects.get(id=int(guild_id.replace("guild_", "").split("_")[-1]))
        if obj and hasattr(obj, 'db') and obj.db.get('guild_name'):
            return obj
    except (ValueError, AttributeError):
        pass
    return None


def get_guild_by_name(name: str) -> Optional[Guild]:
    """Get guild by name."""
    results = search_object(key=f"guild:{name.lower()}", typeclass="world.guilds.Guild")
    return results[0] if results else None


def get_player_guild(player_id: str) -> Optional[Guild]:
    """Get guild a player belongs to."""
    # Search all guilds and check membership
    all_guilds = search_object(typeclass="world.guilds.Guild")
    
    for guild in all_guilds:
        if guild.db.leader == player_id:
            return guild
        members = guild.db.members or {}
        if player_id in members:
            return guild
    
    return None


def is_guild_leader(player_id: str, guild: Guild) -> bool:
    """Check if player is the guild leader."""
    return guild and guild.db.leader == player_id


def is_guild_officer(player_id: str, guild: Guild) -> bool:
    """Check if player is a guild officer."""
    if not guild:
        return False
    if guild.db.leader == player_id:
        return True
    members = guild.db.members or {}
    member_data = members.get(player_id, {})
    return member_data.get("role") in [GUILD_ROLE_LEADER, GUILD_ROLE_OFFICER]


def join_guild(guild: Guild, player_id: str, player_name: str) -> dict:
    """Join a guild (via invitation only for security)."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    members = guild.db.members or {}
    
    if player_id in members:
        return {"success": False, "reason": "Already a member"}
    
    if len(members) >= MAX_GUILD_MEMBERS:
        return {"success": False, "reason": "Guild is full"}
    
    # SECURITY: Require invitation - no open join
    invitations = guild.db.invitations or []
    if player_id not in invitations:
        return {"success": False, "reason": "You must be invited to join this guild"}
    
    # Add member
    members[player_id] = {
        "name": player_name,
        "role": GUILD_ROLE_MEMBER,
        "joined": time.time(),
    }
    guild.db.members = members
    
    # Remove invitation
    if player_id in invitations:
        guild.remove_invitation(player_id)
    
    return {"success": True, "guild": guild.to_dict()}


def leave_guild(guild: Guild, player_id: str) -> dict:
    """Leave a guild."""
    if not guild:
        return {"success": False, "reason": "Not in a guild"}
    
    # Leader can't leave, must disband
    if guild.db.leader == player_id:
        return {"success": False, "reason": "Guild leader cannot leave. Disband the guild instead."}
    
    members = dict(guild.db.members or {})
    if player_id in members:
        del members[player_id]
        guild.db.members = members
        return {"success": True}
    
    return {"success": False, "reason": "Not a member"}


def invite_to_guild(guild: Guild, inviter_id: str, target_id: str) -> dict:
    """Invite a player to the guild."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    # Check permissions
    if not is_guild_officer(inviter_id, guild):
        return {"success": False, "reason": "Not authorized to invite"}
    
    members = guild.db.members or {}
    if target_id in members:
        return {"success": False, "reason": "Already a member"}
    
    invitations = guild.db.invitations or []
    if target_id in invitations:
        return {"success": False, "reason": "Already invited"}
    
    guild.add_invitation(target_id)
    
    return {"success": True}


def kick_from_guild(guild: Guild, kicker_id: str, target_id: str) -> dict:
    """Kick a player from the guild."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    # Check permissions
    if not is_guild_officer(kicker_id, guild):
        return {"success": False, "reason": "Not authorized to kick"}
    
    if guild.db.leader == target_id:
        return {"success": False, "reason": "Cannot kick the leader"}
    
    members = dict(guild.db.members or {})
    if target_id not in members:
        return {"success": False, "reason": "Not a member"}
    
    del members[target_id]
    guild.db.members = members
    
    return {"success": True}


def promote_member(guild: Guild, promoter_id: str, target_id: str, new_role: str) -> dict:
    """Promote/demote a guild member."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    # Only leader can promote to officer
    if new_role == GUILD_ROLE_OFFICER and not is_guild_leader(promoter_id, guild):
        return {"success": False, "reason": "Only leader can promote to officer"}
    
    members = dict(guild.db.members or {})
    if target_id not in members:
        return {"success": False, "reason": "Not a member"}
    
    members[target_id]["role"] = new_role
    guild.db.members = members
    
    return {"success": True}


def set_guild_motd(guild: Guild, player_id: str, motd: str) -> dict:
    """Set guild message of the day."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    if not is_guild_officer(player_id, guild):
        return {"success": False, "reason": "Not authorized"}
    
    guild.set_motd(motd)
    return {"success": True}


def add_guild_zeni(guild: Guild, player_id: str, amount: int) -> dict:
    """Add zeni to guild bank."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    if not is_guild_officer(player_id, guild):
        return {"success": False, "reason": "Not authorized"}
    
    new_balance = guild.add_zeni(amount)
    return {"success": True, "zeni": new_balance}


def withdraw_guild_zeni(guild: Guild, player_id: str, amount: int) -> dict:
    """Withdraw zeni from guild bank."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    if not is_guild_leader(player_id, guild):
        return {"success": False, "reason": "Only leader can withdraw from guild bank"}
    
    if guild.remove_zeni(amount):
        return {"success": True, "zeni": guild.get_zeni()}
    return {"success": False, "reason": "Insufficient funds"}


def deposit_to_guild(guild: Guild, player_id: str, amount: int, player_character) -> dict:
    """Player deposits zeni to guild bank."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    player_zeni = player_character.db.zeni or 0
    if player_zeni < amount:
        return {"success": False, "reason": f"Insufficient funds. You have {player_zeni} zeni."}
    
    # Deduct from player
    player_character.db.zeni = player_zeni - amount
    
    # Add to guild
    new_balance = guild.add_zeni(amount)
    
    return {"success": True, "zeni": new_balance, "player_zeni": player_character.db.zeni}


def disband_guild(guild: Guild, leader_id: str) -> dict:
    """Disband a guild."""
    if not guild:
        return {"success": False, "reason": "Guild not found"}
    
    if guild.db.leader != leader_id:
        return {"success": False, "reason": "Only leader can disband"}
    
    # Delete the guild object
    guild.delete()
    
    return {"success": True}


def list_guilds() -> list:
    """List all guilds."""
    all_guilds = search_object(typeclass="world.guilds.Guild")
    return [
        {
            "id": str(g.id),
            "name": g.db.guild_name,
            "members": len(g.db.members or {}),
            "leader": g._get_leader_name(),
        }
        for g in all_guilds
    ]


def get_guild_members(guild: Guild) -> list:
    """Get list of guild members."""
    if not guild:
        return []
    
    members = []
    for member_id, data in (guild.db.members or {}).items():
        members.append({
            "id": member_id,
            "name": data.get("name", "Unknown"),
            "role": data.get("role", GUILD_ROLE_MEMBER),
            "joined": data.get("joined", 0),
        })
    return members


def get_guild_info(guild: Guild) -> Optional[dict]:
    """Get guild info as dict."""
    if guild:
        return guild.to_dict()
    return None
