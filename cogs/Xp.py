import discord
from discord.ext import commands

class Xp(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_xp(self, u):
        return 0 # Xp amt

    def set_xp(self, u, amt):
        return 0 # Xp amt prev

    def add_xp(self, u, amt):
        return 0 # Xp amt new

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
