import math
import discord
from discord.ext import commands

class Xp(commands.Cog):
    def __init__(self, client):
        self.client = client

    def _get_user(self, u):
        if type(u) is tuple:
            return self.client.get_cog('Main').load_user(u[0], u[1])
        return u

    def get_xp(self, u):
        usr = self._get_user(u)
        return usr.xp # xp

    def set_xp(self, u, amt):
        usr = self._get_user(u)
        old = usr.xp
        usr.xp = amt
        return old # Old xp

    def add_xp(self, u, amt):
        usr = self._get_user(u)
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
