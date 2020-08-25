import discord
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    def _get_user(self, u):
        if type(u) is tuple:
            return self.client.get_cog('Main').load_user(u[0], u[1])
        return u

    def get_balance(self, u):
        usr = self._get_user(u)
        return usr.balance # Balance

    def set_balance(self, u, amt):
        usr = self._get_user(u)
        old = usr.balance
        usr.balance = amt
        return old # Old balance

    def add_balance(self, u, amt):
        usr = self._get_user(u)
        old = usr.balance
        usr.balance = old + amt
        return usr.balance # New balance

    def has_balance(self, u, amt):
        usr = self._get_user(u)
        return usr.balance >= amt

def setup(client):
    client.add_cog(Economy(client))
