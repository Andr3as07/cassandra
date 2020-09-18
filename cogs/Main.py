import discord
import os
import json
from discord.ext import commands

from lib.data import User, Server
from lib import util
from lib import libcassandra as cassandra

class Main(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="profile", help="Shows the profile.")
    async def profile(self, ctx, name = None):
        # Do not do anything on private messages
        if ctx.guild == None:
            return

        uid = ctx.author.id
        if name is not None:
            if name.startswith("<@!") and name.endswith(">"):
                uid = name[3:len(name) - 1]

        usr = cassandra.get_user((ctx.guild.id, uid))
        if usr is None:
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
