import discord
from discord.ext import commands, tasks
from discord.utils import get

UPDATE_TIMEOUT = 3600

class LevelRoles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.update.start()

    @tasks.loop(seconds=UPDATE_TIMEOUT)
    async def update(self):
        print("Processing LevelRank Changes")

        for guild in self.client.guilds:
            # Do not do anything for unavailable guilds
            if guild.unavailable == True:
                continue

            srv = self.client.get_cog('Main').load_server(guild.id)

            # If no level roles are configured, ignore
            if len(srv.level_roles) == 0:
                continue

            # Get all groups into a dictionary
            lv_role_cache = {}
            for lv in srv.level_roles:
                role = get(guild.roles, id=srv.level_roles[lv])
                if role is None:
                    continue
                lv_role_cache[int(lv)] = role
            lv_role_cache = dict(sorted(lv_role_cache.items(), key=lambda item: item[0]))

            for member in guild.members:
                # If member is a bot, ignore
                if member.bot:
                    continue

                level = self.client.get_cog('Xp').get_level((guild.id, member.id))

                highest_role = None
                for lv in lv_role_cache:
                    role = lv_role_cache[lv]
                    if level < lv:
                        break
                    highest_role = role

                if highest_role is None:
                    continue

                if highest_role in member.roles:
                    continue

                print(member.name, level, highest_role)

                for mrole in member.roles:
                    if mrole in lv_role_cache.values():
                        await member.remove_roles(mrole, reason="Userlevel rank")
                await member.add_roles(highest_role, reason="Userlevel change")

                # TODO: Anounce

def setup(client):
    client.add_cog(LevelRoles(client))
