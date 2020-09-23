import discord
from discord.ext import commands

from lib import libcassandra as cassandra
from lib.logging import Logger


class Audit(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    async def print_audit(self, author, type, message):
        self._logger.trace("print_audit")
        usr = cassandra.get_user((author.guild.id, author.id))
        # TODO: Passed user class

        # TODO: Check for user not found

        # Check if the server audit log is enabled
        if usr.server.audit_channel is None:
            return False

        # Check if the audit log channel exists
        ch = self.client.get_channel(usr.server.audit_channel)
        if ch is None:
            return False

        # TODO: Check if audits of this type are enabled

        # Send audit log
        await ch.send("<@!%s>: %s" % (usr.ID, message))

        return True

def setup(client):
    client.add_cog(Audit(client))
