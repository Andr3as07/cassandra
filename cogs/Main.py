import discord
import os
import json
from discord.ext import commands
from lib.data import User, Server
from lib import util

class Main(commands.Cog):
    def __init__(self, client):
        self.client = client

    def load_user(self, srv, uid):
        if type(srv) is int:
            srv = self.load_server(srv)

        print("LOD U %s %s" % (srv.ID, uid))

        usr = User(srv, uid)
        usr.load()
        return usr

    def save_user(self, usr):
        print("SAV U %s %s" % (usr.server.ID, usr.ID))

        usr.save()

        return True

    def load_server(self, sid):
        print("LOD S %s" % sid)

        srv = Server(sid)
        srv.load()

        return srv

    def save_server(self, srv):
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

        content =             ":moneybag: Coins: %s" % usr.balance
        content = content + "\n:star: XP:    %s" % usr.xp
        # content = content + "\n:star2: Level: %s" % usr.level # TODO: FIX

        embed = discord.Embed(
            title = "Profile for %s on server %s" % (discord_user.name, ctx.guild.name),
            description = content,
            colour = discord.Colour.gold()
        )
        embed.set_thumbnail(url=discord_user.avatar_url)

        embed.add_field(name=":writing_hand: Messages", value="Total: %s" % usr.msg_count, inline=True)
        embed.add_field(name=":heart: Reactions", value="Total: %s" % usr.reaction_count, inline=True)
        embed.add_field(name=":microphone2: Voice", value="Time: %s" % util.sec2human(usr.voice_time), inline=True)

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Main(client))
