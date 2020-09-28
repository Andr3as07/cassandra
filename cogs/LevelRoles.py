import discord
from discord.ext import commands, tasks
from discord.utils import get

from lib import libcassandra as cassandra
from lib.logging import Logger

UPDATE_TIMEOUT_SLOW = 3600
UPDATE_TIMEOUT_FAST = 10

class LevelRoles(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

        self._cache_xp_upate = [] # Holds tuples for users to update

    def _build_level_rank_cache(self, guild, srv=None):
        self._logger.trace("_build_level_rank_cache")
        if srv is None:
            srv = cassandra.get_server(guild.id)

        lv_role_cache = {}
        for lv in srv.level_roles:
            role = get(guild.roles, id=srv.level_roles[lv])
            if role is None:
                continue
            lv_role_cache[int(lv)] = role
        return dict(sorted(lv_role_cache.items(), key=lambda item: item[0]))

    async def update_user(self, guild, user, lv_role_cache=None):
        self._logger.trace("update_user")
        if lv_role_cache is None:
            lv_role_cache = self._build_level_rank_cache(guild)

        # If user is a bot, ignore
        if user.bot:
            return

        level = self.client.get_cog('Xp').get_level((guild.id, user.id))

        highest_role = None
        for lv in lv_role_cache:
            role = lv_role_cache[lv]
            if level < lv:
                break
            highest_role = role

        if highest_role is None:
            return

        if highest_role in user.roles:
            return

        for urole in user.roles:
            if urole in lv_role_cache.values():
                await user.remove_roles(urole, reason="Userlevel rank") # TODO: There must be a more efficient way to do this
        await user.add_roles(highest_role, reason="Userlevel change")

        # Dispatch event
        cassandra.dispatch("lvrole-change", {"duser":user,"user":cassandra.get_user((guild.id, user.id)),"role":highest_role})

        # TODO: Anounce

    async def update_guild(self, guild):
        self._logger.trace("update_guild")
        # Do not do anything for unavailable guilds
        if guild.unavailable == True:
            return

        srv = cassandra.load_server(guild.id)

        # If no level roles are configured, ignore
        if len(srv.level_roles) == 0:
            return

        # Get all groups into a dictionary
        lv_role_cache = self._build_level_rank_cache(guild, srv)

        for member in guild.members:
            await self.update_user(guild, member, lv_role_cache)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_slow.start()
        self.update_fast.start()

        cassandra.add_event_listener("xp-change", self, self.on_xp_change)

    def on_xp_change(self, args):
        self._logger.trace("on_xp_change")
        if args.old >= args.new:
            return

        if args.user in self._cache_xp_upate:
            return

        self._cache_xp_upate.append(args.user)

    @tasks.loop(seconds=UPDATE_TIMEOUT_FAST)
    async def update_fast(self):
        if len(self._cache_xp_upate) == 0:
            return

        self._logger.trace("update_fast")

        for entry in self._cache_xp_upate:
            guild = get(self.client.guilds, id=entry.server.ID)
            if guild is None:
                continue

            user = get(guild.members, id=entry.ID)
            if user is None:
                continue

            await self.update_user(guild, user)

        self._cache_xp_upate.clear()

    @tasks.loop(seconds=UPDATE_TIMEOUT_SLOW)
    async def update_slow(self):
        self._logger.trace("update_slow")

        for guild in self.client.guilds:
            await self.update_guild(guild)

def setup(client):
    client.add_cog(LevelRoles(client))
