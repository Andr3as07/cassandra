import discord
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_balance(self, u):
        return 0 # Balance

    def set_balance(self, u, amt):
        return 0 # Balance prev

    def add_balance(self, u, amt):
        return 0 # Balance new

    def has_balance(self, u, amt):
        return False

def setup(client):
    client.add_cog(Economy(client))
