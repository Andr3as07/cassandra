import math
import discord
from discord.ext import commands

from lib import libcassandra as cassandra

class Xp(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_xp(self, u):
        usr = cassandra.get_user(u)
        return usr.xp # xp

    def set_xp(self, u, amt):
        usr = cassandra.get_user(u)
        old = usr.xp

        resp = cassandra.dispatch("xp-change", {"old":old,"new":amt,"user":usr})

        usr.xp = resp.new

        return old # Old xp

    def add_xp(self, u, amt):
        usr = cassandra.get_user(u)
        old = usr.xp
        new = old + amt

        resp = cassandra.dispatch("xp-change", {"old":old,"new":new,"user":usr})

        usr.xp = resp.new
        return usr.xp # New xp

    def get_level(self, u):
        xp = self.get_xp(u)
        lv = 1
        for i in range(2, 100):
            req = math.floor(math.pow(i, 3))
            if req < xp:
                lv = i
            else:
                break
        return lv

def setup(client):
    client.add_cog(Xp(client))
