import discord
import random
import json
import os
from discord.ext import commands

from lib.logging import Logger

EMOJI_A = "🅰"
EMOJI_B = "🅱"
EMOJI_8BALL = "🎱"

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

        self.wyr_data = []
        self.whatami_data = []
        self.eightball_data = []
        self.fortunes = {}

        self._load_wyr_assets()
        self._load_fortune_assets()
        self._load_whatami_assets()
        self._load_8ball_assets()

    def _load_wyr_assets(self):
        path = "assets/wyr.json"

        if not os.path.exists(path):
            return False

        with open(path) as f:
            jdata = json.load(f)

            self.wyr_data = jdata["questions"]

            self._logger.info("Loaded WYR Data")
            return True

    def _load_fortune_assets(self):
        dir_path = "assets/fortunes"

        if not os.path.exists(dir_path):
            return False

        for filename in os.listdir(dir_path):
            if not filename.endswith(".json"):
                continue

            path = dir_path + "/" + filename
            with open(path) as f:
                jdata = json.load(f)

                self.fortunes[filename[:-5]] = jdata["fortunes"]
                self._logger.info("Loaded fortune database %s" % filename)

        self._logger.info("Loaded fortune Data")
        return True

    def _load_whatami_assets(self):
        path = "assets/whatami.json"

        if not os.path.exists(path):
            return False

        with open(path) as f:
            jdata = json.load(f)

            self.whatami_data = jdata["quotes"]

        self._logger.info("Loaded whatami Data")
        return True

    def _load_8ball_assets(self):
        path = "assets/8ball.json"

        if not os.path.exists(path):
            return False

        with open(path) as f:
            jdata = json.load(f)

            self.eightball_data = jdata["answers"]

        self._logger.info("Loaded 8ball Data")
        return True

    def get_help_page(self):
        return {
            "title": "Fun Commands",
            "description": None,
            "content": {
                "8ball <Question ...>": "Ask the magic 8ball.",
                #"conn <User>": "Starts a game of connect-4 against the mentioned user.",
                "fortune": "Opens a fortune cookie.",
                #"rusr": "Plays a round of russian roulette.",
                #"tord": "Play a game of truth or dare.",
                #"ttt <User>": "Starts a game of Tick-Tack-Toe.",
                "wyr": "Displays a would you rather question.",
                "whatami": "You better have thick skin...or a thick skull!"
            }
        }

    @commands.command(name="whatami")
    async def whatami(self, ctx):
        self._logger.trace("whatami")
        quote = random.choice(self.whatami_data)
        await ctx.send(quote)

    @commands.command(name="conn")
    async def conn(self, ctx):
        self._logger.trace("conn")
        await ctx.send("Not implemented")

    @commands.command(name="fortune")
    async def fortune(self, ctx):
        self._logger.trace("fortune")

        # TODO: Handle dictionary is empty

        db = random.choice(list(self.fortunes.keys()))

        # TODO: Handle db is empty

        line = random.choice(self.fortunes[db])

        await ctx.send(line)

    @commands.command(name="tord")
    async def tord(self, ctx):
        self._logger.trace("tord")
        await ctx.send("Not implemented")

    @commands.command(name="ttt")
    async def ttt(self, ctx):
        self._logger.trace("ttt")
        await ctx.send("Not implemented")

    @commands.command(name="wyr")
    async def wyr(self, ctx):
        self._logger.trace("wyr")
        line = random.choice(self.wyr_data)

        embed = discord.Embed(
            title = "Would You Rather",
            description = "**" + line["question"] + "**\n\n\n" + EMOJI_A + " " + line["answer_1"] + "\n\n" + EMOJI_B + " " + line["answer_2"],
            colour = discord.Colour.red()
        )

        msg = await ctx.send(embed=embed)

        await msg.add_reaction(EMOJI_A)
        await msg.add_reaction(EMOJI_B)

    @commands.command(name="8ball")
    async def eightball(self, ctx):
        self._logger.trace("8ball")
        await ctx.send(EMOJI_8BALL + " " + random.choice(self.eightball_data))

def setup(client):
    client.add_cog(Fun(client))
