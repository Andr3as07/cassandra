import os
import json

class CassandraConfig:
    def __init__(self, path):
        self.path = path

        self.cogs = {}

    def load(self):
        if not os.path.isfile(self.path):
            return False

        with open(self.path) as f:
            jdata = json.load(f)

            if "cogs" in jdata:
                jcogs = jdata["cogs"]
                for cogname in jcogs:
                    jcog = jcogs[cogname]
                    cog = CassandraConfigCog(cogname)

                    if "autoload" in jcog:
                        cog.autoload = jcog["autoload"]

                    self.cogs[cogname] = cog

        return True

class CassandraConfigCog:
    def __init__(self, name):
        self.name = name
        self.autoload = False

class Server:
    def __init__(self, id):
        self.ID = id

        self.prefix_used = '$'
        self.prefix_blocked = []

        self.audit_channel = None
        self.audit_log_clear = True
        self.audit_log_warn = True
        self.audit_log_kick = True
        self.audit_log_ban = True

        self.tickets_channel_updates = None
        self.tickets_channel_closed = None
        self.tickets_category = None
        self.tickets_roles_admin = []
        self.tickets_roles_moderator = []
        self.tickets_next_id = 1
        self.tickets = []

        self.role_commands = []

        self.level_roles = {}
        self.level_roles_channel = None

        self.autochannel_router = None
        self.autochannel_channels = []

        self.quarantine_role = None

    def _get_dir_path(self):
        return "data/%s" % self.ID

    def _get_path(self):
        return "data/%s/config.json" % self.ID

    def load(self):
        path = self._get_path()

        if not os.path.isfile(path):
            return False

        with open(path) as f:
            jdata = json.load(f)

            # Prefix
            if "prefix_used" in jdata:
                self.prefix_used = jdata["prefix_used"]

            # Ignored Prefixes
            if "prefix_blocked" in jdata:
                self.prefix_blocked = jdata["prefix_blocked"]

            # Audit Settings
            if "audit" in jdata:
                self.audit_channel = jdata["audit"]["channel"]
                self.audit_log_clear = jdata["audit"]["clear"]
                self.audit_log_warn = jdata["audit"]["warn"]
                self.audit_log_kick = jdata["audit"]["kick"]
                self.audit_log_ban = jdata["audit"]["ban"]

            # Tickets
            if "tickets" in jdata:
                if "channel_closed" in jdata["tickets"]:
                    self.tickets_channel_closed = jdata["tickets"]["channel_closed"]
                if "channel_updates" in jdata["tickets"]:
                    self.tickets_channel_updates = jdata["tickets"]["channel_updates"]
                if "category" in jdata["tickets"]:
                    self.tickets_category = jdata["tickets"]["category"]

                # Parse tickets
                if "list" in jdata["tickets"]:
                    jlist = jdata["tickets"]["list"]

                    for ticket_id, jticket in jlist.items():
                        ticket = Ticket(self, int(ticket_id), jticket["name"])

                        if "admin_only" in jticket:
                            ticket.admin_only = jticket["admin_only"]
                        if "status" in jticket:
                            ticket.status = jticket["status"]
                        if "users" in jticket:
                            ticket.users = jticket["users"]
                        if "channel" in jticket:
                            ticket.channel = jticket["channel"]

                        self.tickets.append(ticket)

                self.tickets_next_id = len(self.tickets) + 1

            # Quarantine
            if "quarantine_role" in jdata:
                self.quarantine_role = jdata["quarantine_role"]

            # Autochannels
            if "auto_channel" in jdata:
                if "router" in jdata["auto_channel"]:
                    self.autochannel_router = jdata["auto_channel"]["router"]

                if "channels" in jdata["auto_channel"]:
                    self.autochannel_channels = jdata["auto_channel"]["channels"]

            # Level Roles
            if "level_roles" in jdata:
                jlrdata = jdata["level_roles"]

                # TODO: Channel

                # Levels
                if "level" in jlrdata:
                    for lv in jlrdata["level"]:
                        self.level_roles[lv] = jlrdata["level"][lv]

            # Role Commands
            if "role_commands" in jdata:
                rc = jdata["role_commands"]

                for groupname in rc:
                    group = RoleGroup(groupname)
                    jgroup = rc[groupname]

                    if "timelimit" in jgroup:
                        group.timelimit = jgroup["timelimit"]

                    if "mode" in jgroup:
                        group.mode = jgroup["mode"]

                    if group.mode == "single":
                        group.autoremove = jgroup["autoremove"]
                    elif group.mode == "multiple":
                        group.max = jgroup["max"]


                    for rolename in jgroup["roles"]:
                        role = RoleCommand(rolename)
                        jrole = jgroup["roles"][rolename]

                        role.role = jrole["role"]
                        role.requires = jrole["requires"]

                        group.roles.append(role)

                    self.role_commands.append(group)

        return True

    def save(self):
        path = self._get_path()

        os.makedirs(self._get_dir_path(), exist_ok=True)

        with open(path, 'w') as f:
            data = {
                'prefix_used': self.prefix_used,
                'prefix_blocked': self.prefix_blocked,
                'quarantine_role': self.quarantine_role,
                'audit': {
                    'channel': self.audit_channel,
                    'ban': self.audit_log_ban,
                    'clear': self.audit_log_clear,
                    'kick': self.audit_log_kick,
                    'warn': self.audit_log_warn
                },
                'tickets': {
                    'category': self.tickets_category,
                    'channel_closed': self.tickets_channel_closed,
                    'channel_updates': self.tickets_channel_updates,
                    'roles_admin': self.tickets_roles_admin,
                    'roles_moderator': self.tickets_roles_moderator
                },
                'level_roles': {
                    'channel': self.level_roles_channel,
                    'level': self.level_roles
                },
                "auto_channel": {
                    "router": self.autochannel_router,
                    "channels": self.autochannel_channels
                },
                'role_commands': {}
            }

            # Tickets list
            tlist = {}
            for ticket in self.tickets:
                tentry = {
                    'admin_only': ticket.admin_only,
                    'channel': ticket.channel,
                    'id': ticket.ID,
                    'name': ticket.name,
                    'status': ticket.status,
                    'users': ticket.users
                }
                tlist[ticket.ID] = tentry
            data["tickets"]["list"] = tlist

            # Role commands
            rgroups = {}
            for rgroup in self.role_commands:
                rgroupdata = {
                    'mode': rgroup.mode,
                    'timelimit': rgroup.timelimit,
                    'requires': rgroup.requires
                }
                if rgroup.mode == "multiple":
                    rgroupdata["max"] = rgroup.max
                elif rgroup.mode == "single":
                    rgroupdata["autoremove"] = rgroup.autoremove

                rolelist = {}
                for role in rgroup.roles:
                    roledata = {
                        'role': role.role,
                        'requires': role.requires
                    }
                    rolelist[role.name] = roledata
                rgroupdata["roles"] = rolelist
                rgroups[rgroup.name] = rgroupdata
            data["role_commands"] = rgroups

            json.dump(data, f, indent=2, sort_keys=True)

            return True

        return False # We should never end up here

class RoleGroup:
    def __init__(self, name):
        self.name = name

        self.timelimit = None
        self.requires = []

        self.roles = []

        self.mode = "none" # none/single/multiple

        # multiple
        self.max = None

        # single
        self.autoremove = False

class RoleCommand:
    def __init__(self, name):
        self.name = name
        self.role = None
        self.requires = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

class Ticket:
    def __init__(self, server, id, name, channel=None, admin_only=False, users=[], status="unknown"):
        self.server = server
        self.ID = id
        self.name = name

        self.channel = channel
        self.admin_only = admin_only
        self.users = users
        self.status = status

class User:
    def __init__(self, server, id):
        self.server = server
        self.ID = id

        self.balance = 0
        self.xp = 0

        self.msg_last = 0
        self.msg_awarded = 0
        self.msg_count = 0

        self.reaction_last = 0
        self.reaction_awarded = 0
        self.reaction_count = 0

        self.voice_time = 0

        self.history = []

        self.nicknames = []
        self.names = []

        self.casino_last_spin = 0

    def _get_path(self):
        return "data/%s/%s.json" % (self.server.ID, self.ID)

    def _get_dir_path(self):
        return "data/%s" % self.server.ID

    def load(self):
        path = self._get_path()

        if not os.path.isfile(path):
            return False

        with open(path) as f:
            jdata = json.load(f)

            # Balance
            if "balance" in jdata:
                self.balance = jdata["balance"]
            elif "coins" in jdata:
                self.balance = jdata["coins"]

            # xp
            if "xp" in jdata:
                self.xp = jdata["xp"]

            # msg
            if "msg" in jdata:
                self.msg_last = jdata["msg"]["last"]
                self.msg_awarded = jdata["msg"]["awarded"]
                self.msg_count = jdata["msg"]["count"]

            # msg
            if "reaction" in jdata:
                self.reaction_last = jdata["reaction"]["last"]
                self.reaction_awarded = jdata["reaction"]["awarded"]
                self.reaction_count = jdata["reaction"]["count"]

            # voice
            if "voice" in jdata:
                self.voice_time = jdata["voice"]["time"]

            # cassino
            if "cassino" in jdata:
                self.cassino_last_spin = jdata["cassino"]["last_spin"]

            # TODO: History
            if "history" in jdata:
                self.history = jdata["history"] # TODO: Actualy parse this data

            # TODO: Nicknames
            if "nicknames" in jdata:
                self.nicknames = jdata["nicknames"] # TODO: Actualy parse this data

            # TODO: Names
            if "names" in jdata:
                self.names = jdata["names"] # TODO: Actualy parse this data

        return True

    def save(self):
        path = self._get_path()

        os.makedirs(self._get_dir_path(), exist_ok=True)

        with open(path, 'w') as f:
            data = {
                'sid': self.server.ID,
                'uid': self.ID,
                'balance': self.balance,
                'xp': self.xp,
                'msg': {
                    'last': self.msg_last,
                    'awarded': self.msg_awarded,
                    'count': self.msg_count
                },
                'reaction': {
                    'last': self.reaction_last,
                    'awarded': self.reaction_awarded,
                    'count': self.reaction_count
                },
                'voice': {
                    'time': self.voice_time
                },
                'history': self.history, # To be filled later
                'nicknames': self.nicknames, # To be filled later
                'names':  self.names, # To be filled later
                'casino': {
                    'last_spin': self.casino_last_spin
                }
            }

            json.dump(data, f, indent=2, sort_keys=True)

            return True

        return False # We should never end up here
