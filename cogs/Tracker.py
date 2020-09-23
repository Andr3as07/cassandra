import discord
from discord.ext import commands, tasks

from lib import libcassandra as cassandra
from lib.logging import Logger

UPDATE_TIMEOUT = 3600

class Tracker(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    def get_nicknames(self, u):
        self._logger.trace("get_nicknames")
        usr = cassandra.get_user(u)
        return usr.nicknames

    def get_names(self, u):
        self._logger.trace("get_names")
        usr = cassandra.get_user(u)
        return usr.names

    def add_nickname(self, u, dusr):
        self._logger.trace("add_nickname")
        usr = cassandra.get_user(u)

        if dusr.nick is None:
            return False # Has no nick

        if dusr.nick in usr.nicknames:
            # Dispatch event
            cassandra.dispatch("nickname-change", {"user":usr,"nick":dusr.nick,"known":True})
            return False # Known nick

        # Dispatch event
        cassandra.dispatch("nickname-change", {"user":usr,"nick":dusr.nick,"known":False})

        usr.nicknames.append(dusr.nick)

        return True # New nick

    def add_name(self, u, dusr):
        self._logger.trace("add_name")
        usr = cassandra.get_user(u)

        name = dusr.name + "#" + dusr.discriminator

        if name in usr.names:
            # Dispatch event
            cassandra.dispatch("name-change", {"user":usr,"name":name,"known":True})
            return False # Known name

        # Dispatch event
        cassandra.dispatch("name-change", {"user":usr,"name":dusr.nick,"known":False})

        usr.names.append(name)

        return True # New name

    @commands.Cog.listener()
    async def on_ready(self):
        self.update.start()

    @commands.command(name="whois")
    @commands.has_permissions(manage_messages=True)
    async def whois(self, ctx, member : discord.Member):
        self._logger.trace("whois")
        usr = cassandra.get_user((ctx.guild.id, member.id))
        if usr is None:
            await ctx.send("Couldn't get user information")
            return

        title = "%s#%s" % (member.name, member.discriminator)
        if member.nick is not None:
            title = title + ("(%s)" % member.nick)

        nicknames = "No nicknames tracked"
        nicklist = self.get_nicknames(usr)
        if len(nicklist) > 0:
            nicknames = "```" + ', '.join(nicklist) + '```'

        names = "No names tracked"
        namelist = self.get_names(usr)
        if len(namelist) > 0:
            names = "```" + ', '.join(namelist) + '```'

        embed = discord.Embed(
            title = title
        )
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(name="ID", value=str(member.id))
        embed.add_field(name="Account Created", value=str(member.created_at), inline=True)
        embed.add_field(name="Joined At", value=str(member.joined_at), inline=True)
        embed.add_field(name="Nicknames", value=nicknames)
        embed.add_field(name="Names", value=names)

        await ctx.send(embed=embed)

    @commands.Cog.listener() # Username, discriminator
    async def on_member_join(self, member):
        self._logger.trace("on_member_join")
        usr = cassandra.get_user((member.guild.id, member.id))

        update = False

        if self.add_name(usr, member):
            update = True

        if self.add_nickname(usr, member):
            update = True

        if update:
            cassandra.save_user(usr)

    @commands.Cog.listener() # Nickname
    async def on_member_update(self, before, after):
        self._logger.trace("on_member_update")
        usr = cassandra.get_user((after.guild.id, after.id))

        if self.add_nickname(usr, after):
            cassandra.save_user(usr)

    @commands.Cog.listener() # Username, discriminator
    async def on_user_join(self, member):
        usr = cassandra.get_user((member.guild.id, member.id))

        if self.add_nickname(usr, member):
            cassandra.save_user(usr)

    @tasks.loop(seconds=UPDATE_TIMEOUT)
    async def update(self):
        self._logger.trace("update")

        for guild in self.client.guilds:
            # Do not do anything for unavailable guilds
            if guild.unavailable == True:
                continue

            for member in guild.members:
                # If member is a bot, ignore
                if member.bot:
                    continue

                usr = cassandra.get_user((guild.id, member.id))
                self.add_nickname(usr, member)
                self.add_name(usr, member)

def setup(client):
    client.add_cog(Tracker(client))
