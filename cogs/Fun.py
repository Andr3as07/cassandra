import discord
import random
import json
import os
from discord.ext import commands

EMOJI_A = "🅰"
EMOJI_B = "🅱"
EMOJI_8BALL = "🎱"

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.wyr_data = []
        self._load_wyr_assets()

    def _load_wyr_assets(self):
        path = "assets/wyr.json"

        if not os.path.exists(path):
            return False

        with open(path) as f:
            jdata = json.load(f)

            self.wyr_data = jdata["questions"]

            return True

    def get_help_page(self):
        return {
            "title": "Fun Commands",
            "description": None,
            "content": {
                "8ball <Question ...>": "Ask the magic 8ball.",
                #"conn <User>": "Starts a game of connect-4 against the mentioned user.",
                #"fortune": "Opens a fortune cookie.",
                #"rusr": "Plays a round of russian roulette.",
                #"tord": "Play a game of truth or dare.",
                #"ttt <User>": "Starts a game of Tick-Tack-Toe.",
                "wyr": "Displays a would you rather question.",
            }
        }

    @commands.command(name="conn")
    async def conn(self, ctx):
        await ctx.send("Not implemented")

    @commands.command(name="fortune")
    async def fortune(self, ctx):
        await ctx.send("Not implemented")

    @commands.command(name="tord")
    async def tord(self, ctx):
        await ctx.send("Not implemented")

    @commands.command(name="ttt")
    async def ttt(self, ctx):
        await ctx.send("Not implemented")

    @commands.command(name="wyr")
    async def wyr(self, ctx):
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
    async def eight_ball(self, ctx):
        answers = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes – definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",

            "Reply hazy, try again."
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",

            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        await ctx.send(EMOJI_8BALL + " " + random.choice(answers))

def setup(client):
    client.add_cog(Fun(client))
