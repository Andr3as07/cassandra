import os
import json

class Server:
    def __init__(self, id):
        self.ID = id

        self.prefix_used = '$'
        self.prefix_blocked = []

        self.audit_channel = None
        self.audit_log_clear = True
        self.audit_log_warn = True
        self.audit_log_kick = True
        self.audit_log_block = True

        self.roles_admin = []
        self.roles_mod = []

        self.tickets_channel_updates = None
        self.tickets_channel_closed = None
        self.tickets_next_id = 1
        self.tickets = []

        self.role_commands = []

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
                self.audit_log_block = jdata["audit"]["block"]

            # Roles list
            if "roles_admin" in jdata:
                self.roles_admin = jdata["roles_admin"]
            if "roles_mod" in jdata:
                self.roles_mod = jdata["roles_mod"]

            # Tickets
            if "tickets" in jdata:
                if "tickets_channel_closed" in jdata["tickets"]:
                    self.tickets_channel_closed = jdata["tickets"]["chennel_closed"]
                if "tickets_channel_updates" in jdata["tickets"]:
                    self.tickets_channel_updates = jdata["tickets"]["chennel_updates"]

                # TODO: Parse tickets

                self.tickets_next_id = self.tickets.length() + 1

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

class RoleGroup:
    def __init__(self, name):
        self.name = name

        self.timelimit = None
        self.requires = []

        self.roles = []

        self.type = "none" # none/single/multiple

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
    def __init__(self, server, id):
        self.server = server
        self.ID = id

        self.name = None
        self.channel = None
        self.admin_only = False
        self.users = []
        self.status = "unknown"

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
