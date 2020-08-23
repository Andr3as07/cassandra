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

    def load(self):
        return True # TODO: Implement

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

            if "balance" in jdata:
                self.balance = jdata["balance"]
            elif "coins" in jdata:
                self.balance = jdata["coins"]

            if "xp" in jdata:
                self.xp = jdata["xp"]

        return True

    def save(self):
        path = self._get_path()

        os.makedirs(self._get_dir_path(), exists_ok=True)

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
                'history': [], # To be filled later
                'nicknames': [], # To be filled later
                'names': [], # To be filled later
                'casino': {
                    'last_spin': self.casino_last_spin
                }
            }

            json.dump(data, f, indent=2, sort_keys=True)

            return True

        return False # We should never end up here
