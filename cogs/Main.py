import discord
import os
import json
from discord.ext import commands
from lib.data import User, Server
from lib import util

class Main(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.cache_usr = {}
        self.cache_srv = {}

    def load_user(self, srv, uid):
        # Load server if needed
        if type(srv) is int:
            srv = self.load_server(srv)

        # Cache lookup
        cache_id = "%s:%s" % (srv.ID, uid)
        if cache_id in self.cache_usr:
            return self.cache_usr[cache_id]

        print("LOD U %s %s" % (srv.ID, uid))
        usr = User(srv, uid)
        usr.load()

        # Populate cache
        self.cache_usr[cache_id] = usr

        return usr

    def save_user(self, usr):
        print("SAV U %s %s" % (usr.server.ID, usr.ID))
        usr.save()

        # Remove from cache
        self.cache_usr.pop(usr.ID, None)

        return True

    def load_server(self, sid):
        # Cache lookup
        if sid in self.cache_srv:
            return self.cache_srv[sid]

        print("LOD S %s" % sid)
        srv = Server(sid)
        srv.load()

        # Populate cache
        self.cache_srv[sid] = srv

        return srv

    def save_server(self, srv):
        # Remove from cache
        self.cache_srv.pop(srv.ID, None)

        # TODO: Implement
        return False


    @commands.command(name="profile", help="Shows the profile.")
    async def profile(self, ctx, name = None):
        # Do not do anything on private messages
        if ctx.guild == None:
            return

        uid = ctx.author.id
        if name is not None:
            if name.startswith("<@!") and name.endswith(">"):
                uid = name[3:len(name) - 1]

        usr = self.load_user(ctx.guild.id, uid)
        if usr == None:
            await ctx.send("User not found.")
            return

        discord_user = self.client.get_user(usr.ID)
        if discord_user is None:
            await ctx.send("User not found.")
            return

        content = ""
        cecon = self.client.get_cog('Economy')
        if cecon is not None:
            content = content + ":moneybag: Coins: %s" % cecon.get_balance(usr)

        cxp = self.client.get_cog('Xp')
        if cxp is not None:
            content = content + "\n:star: XP:    %s" % cxp.get_xp(usr)
            content = content + "\n:star2: Level: %s" % cxp.get_level(usr)

        embed = discord.Embed(
            title = "Profile for %s on server %s" % (discord_user.name, ctx.guild.name),
            description = content,
            colour = discord.Colour.gold()
        )
        embed.set_thumbnail(url=discord_user.avatar_url)

        stats = self.client.get_cog('Stats')
        if stats is not None:
            embed.add_field(name=":writing_hand: Messages", value="Total: %s" % stats.get_msg(usr), inline=True)
            embed.add_field(name=":heart: Reactions", value="Total: %s" % stats.get_reaction(usr), inline=True)
            embed.add_field(name=":microphone2: Voice", value="Time: %s" % util.sec2human(stats.get_voice(usr)), inline=True)

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Main(client))
