import discord
from discord.ext import commands

from lib import libcassandra as cassandra

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_balance(self, u):
        usr = cassandra.get_user(u)
        return usr.balance # Balance

    def set_balance(self, u, amt):
        usr = cassandra.get_user(u)
        old = usr.balance
        usr.balance = amt
        return old # Old balance

    def add_balance(self, u, amt):
        usr = cassandra.get_user(u)
        old = usr.balance
        usr.balance = old + amt
        return usr.balance # New balance

    def has_balance(self, u, amt):
        usr = cassandra.get_user(u)
        return usr.balance >= amt

def setup(client):
    client.add_cog(Economy(client))
