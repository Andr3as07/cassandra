import discord
from discord.ext import commands, tasks
from lib import util

from lib import libcassandra as cassandra
from lib.logging import Logger

MSG_TIMEOUT = 60
MSG_BONUS_COINS = 1
MSG_BONUS_XP = 5

REACTION_TIMEOUT = 60
REACTION_BONUS_COINS = 1
REACTION_BONUS_XP = 1

VOICE_TIMEOUT = 5 * 60
VOICE_BONUS_COINS = 1
VOICE_BONUS_XP = 2

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    def get_msg(self, u):
        self._logger.trace("get_msg")
        usr = cassandra.get_user(u)
        return usr.msg_count

    def get_reaction(self, u):
        self._logger.trace("get_reaction")
        usr = cassandra.get_user(u)
        return usr.reaction_count

    def get_voice(self, u):
        self._logger.trace("get_voice")
        usr = cassandra.get_user(u)
        return usr.voice_time

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_voice.start()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        self._logger.trace("on_reaction_add")
        # Ignore reactions from bots
        if user.bot == True:
            return

        # Ignore private messages
        if reaction.message.guild is None:
            return

        # Ignore reactions made to messages written by bots
        if reaction.message.author.bot == True:
            return

        usr = cassandra.get_user((reaction.message.guild.id, user.id))

        # TODO: Handle user not found

        ts = util.getts()
        usr.reaction_last = ts

        # if reaction timeout is reached award coins
        if ts - usr.reaction_awarded > REACTION_TIMEOUT:
            usr.reaction_awarded = ts

            # Add balance if economy cog is loaded
            cecon = self.client.get_cog('Economy')
            if cecon is not None:
                cecon.add_balance(usr, REACTION_BONUS_COINS)

            # Add xp if xp cog is loaded
            cxp = self.client.get_cog('Xp')
            if cxp is not None:
                cxp.add_xp(usr, REACTION_BONUS_XP)

        usr.reaction_count = usr.reaction_count + 1

        cassandra.save_user(usr)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot == True:
            return

        # Ignore direct messages
        if message.guild is None:
            return

        self._logger.trace("on_message(%s)" % message.content)

        srv = cassandra.get_server(message.guild.id)
        # TODO: Check if server is not found

        # Ignore commands to cassandra
        if message.content.startswith(srv.prefix_used):
            return

        # Ignore commands to other bots
        for prefix in srv.prefix_blocked:
            if message.content.startswith(prefix):
                return

        usr = cassandra.get_user((srv, message.author.id))
        # TODO: Check if user is not found

        ts = util.getts()
        usr.msg_last = ts
        usr.msg_count = usr.msg_count + 1

        #if msg timeout is reached award coins
        if ts - usr.msg_awarded > MSG_TIMEOUT:
            usr.msg_awarded = ts

            # Add balance if economy cog is loaded
            cecon = self.client.get_cog('Economy')
            if cecon is not None:
                cecon.add_balance(usr, MSG_BONUS_COINS)

            # Add xp if xp cog is loaded
            cxp = self.client.get_cog('Xp')
            if cxp is not None:
                cxp.add_xp(usr, MSG_BONUS_XP)

        cassandra.save_user(usr)

    @tasks.loop(seconds=VOICE_TIMEOUT)
    async def update_voice(self):
        self._logger.trace("update_voice")

        # For all voice channels on each guild
        for guild in self.client.guilds:

            # Do not do anything for unavailable guilds
            if guild.unavailable == True:
                continue

            # For each voice channel in each guild
            for vchannel in guild.voice_channels:
                vchmem = len(vchannel.members)

                # No need to look into a voice channel with one or no active members
                if vchmem < 2:
                    continue

                # For each current member
                for member in vchannel.members:
                    if member.voice.afk:
                        continue
                    elif member.voice.deaf or member.voice.self_deaf:
                        continue
                    elif member.voice.mute or member.voice.self_mute:
                        continue

                    usr = cassandra.get_user((guild.id, member.id))
                    usr.voice_time = usr.voice_time + VOICE_TIMEOUT

                    # Add balance if economy cog is loaded
                    cecon = self.client.get_cog('Economy')
                    if cecon is not None:
                        cecon.add_balance(usr, VOICE_BONUS_COINS)

                    # Add xp if xp cog is loaded
                    cxp = self.client.get_cog('Xp')
                    if cxp is not None:

                        # Give an xp bonus for more people in the voicechat
                        xp = VOICE_BONUS_XP + (vchmem - 2)
                        cxp.add_xp(usr, xp)

                    cassandra.save_user(usr)

def setup(client):
    client.add_cog(Stats(client))
