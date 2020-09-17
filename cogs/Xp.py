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
        usr.xp = amt
        return old # Old xp

    def add_xp(self, u, amt):
        usr = cassandra.get_user(u)
        old = usr.xp
        usr.xp = old + amt
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
