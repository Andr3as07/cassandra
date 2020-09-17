import discord
from discord.ext import commands, tasks

from lib import libcassandra as cassandra

UPDATE_TIMEOUT = 3600

class Tracker(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_nicknames(self, u):
        usr = cassandra.get_user(u)
        return usr.nicknames

    def get_names(self, u):
        usr = cassandra.get_user(u)
        return usr.names

    def add_nickname(self, u, dusr):
        usr = cassandra.get_user(u)

        if dusr.nick is None:
            return False # Has no nick

        if dusr.nick in usr.nicknames:
            return False # Known nick

        usr.nicknames.append(dusr.nick)

        return True # New nick

    def add_name(self, u, dusr):
        usr = cassandra.get_user(u)

        name = dusr.name + "#" + dusr.discriminator

        if name in usr.names:
            return False # Known name

        usr.names.append(name)

        return True # New name

    @commands.Cog.listener()
    async def on_ready(self):
        self.update.start()

    @commands.command(name="whois")
    @commands.has_permissions(manage_messages=True)
    async def whois(self, ctx, member : discord.Member):
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
        print("Processing Nickname Changes")

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
