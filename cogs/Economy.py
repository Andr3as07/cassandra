import discord
from discord.ext import commands

from lib import libcassandra as cassandra
from lib.logging import Logger

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    def get_balance(self, u):
        self._logger.trace("get_balance")
        usr = cassandra.get_user(u)
        return usr.balance # Balance

    def set_balance(self, u, amt):
        self._logger.trace("set_balance")
        usr = cassandra.get_user(u)
        old = usr.balance

        resp = cassandra.dispatch("balance-change", {"old":old,"new":amt,"user":usr})

        usr.balance = resp.new
        return old # Old balance

    def add_balance(self, u, amt):
        self._logger.trace("add_balance")
        usr = cassandra.get_user(u)
        old = usr.balance

        resp = cassandra.dispatch("balance-change", {"old":old,"new":old+amt,"user":usr})

        usr.balance = resp.new
        return usr.balance # New balance

    def has_balance(self, u, amt):
        self._logger.trace("has_balance")
        usr = cassandra.get_user(u)
        return usr.balance >= amt

def setup(client):
    client.add_cog(Economy(client))
