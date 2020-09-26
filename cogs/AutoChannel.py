import discord

from discord.ext import commands
from discord.utils import get

from lib import util
from lib import libcassandra as cassandra
from lib.logging import Logger

class AutoChannel(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    async def create_autochannel(self, s, dguild, duser=None):
        srv = cassandra.get_server(s)

        # Check if autochannels are configured
        if srv.autochannel_router is None:
            self._logger.debug("router channel not configured")
            return False

        # Find router channel
        router = get(dguild.channels, id=srv.autochannel_router)
        if router is None:
            self._logger.debug("router channel not found")
            return False

        # Get category
        cat = router.category
        if cat is None:
            self._logger.debug("router channel has no category")
            return False

        name = "Autochannel"
        if duser is not None:
            name = "AC %s" % (duser.display_name)
        channel = await cat.create_voice_channel(name, reason="New AutoChannel")

        # Save changes
        srv.autochannel_channels.append(channel.id)
        cassandra.save_server(srv)

        # Move member to new channel
        if duser is not None:
            await duser.edit(voice_channel=channel)

        return True

    async def delete_autochannel(self, s, dguild, channel):
        srv = cassandra.get_server(s)

        if not channel.id in srv.autochannel_channels:
            self._logger.debug("channel not an autochannel")
            return False

        # Check if the channel is empty
        if len(channel.members) > 0:
            self._logger.debug("still still users in channel")
            return False

        # Remove from server data
        srv.autochannel_channels.remove(channel.id)
        cassandra.save_server(srv)

        # Delete empty channel
        await channel.delete(reason="Empty AutoChannel")

        return True

    async def cleanup(self, guild=None):
        self._logger.trace("cleanup(%s)" % guild)
        if guild is None:
            # For all guilds
            for g in self.client.guilds:
                # Do not do anything for unavailable guilds
                if g.unavailable == True:
                    continue

                self.cleanup(g)

        else:
            srv = cassandra.get_server(guild.id)
            for ac in srv.autochannel_channels:
                channel = get(guild.channels, id=ac)
                if channel is None:
                    continue

                await self.delete_autochannel(srv, guild, channel)

    @commands.command(name="autochannel")
    @commands.has_permissions(manage_channels=True)
    async def autochannel(self, ctx, action, router=None):
        self._logger.trace("autochannel")

        srv = cassandra.get_server(ctx.guild.id)
        if action in ["disable", "stop"]:
            srv.autochannel_router = None
            cassandra.save_server(srv)

            await self.cleanup()

            await ctx.send("Autochannels are no longer active.\nIf you want to use them in the future, you need to configure them again.")

        elif action in ["setup", "start", "enable"]:
            if router is None:
                return # TODO: Print help

            routerid = None
            try:
                routerid = int(router)
            except Exception:
                return # TODO: User feedback

            routerch = get(ctx.guild.channels, id=routerid)
            if routerch is None:
                return # TODO: User feedback

            if routerch.category is None:
                await ctx.send("The autochannel router must be part of a channel category!")
                return

            srv.autochannel_router = routerid
            cassandra.save_server(srv)

            await ctx.send("Autochannels successfully configured.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        srv = cassandra.get_server(member.guild.id)

        if after.channel is not None:
            if after.channel.id == srv.autochannel_router:
                self._logger.debug("user join router")
                await self.create_autochannel(srv, member.guild, member)

        elif before.channel is not None:
            if before.channel.id in srv.autochannel_channels:
                self._logger.debug("user left autochannel")
                await self.delete_autochannel(srv, member.guild, before.channel)

    @commands.Cog.listener()
    async def on_ready(self):
        self._logger.trace("on_ready")
        await self.cleanup()

def setup(client):
    client.add_cog(AutoChannel(client))
