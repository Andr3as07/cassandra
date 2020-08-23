import discord
import random
from discord.ext import commands

EMOJI_A = "🅰"
EMOJI_B = "🅱"
EMOJI_8BALL = "🎱"

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

        # TODO: Load wyr data
        self.wyr_data = [
            ["Would you rather Swim 300 meters through shit or dead bodies?", "Swim 300 meters through shit", "Swim 300 meters through dead bodies"]
        ]

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
        question = random.choice(self.wyr_data)

        embed = discord.Embed(
            title = "Would You Rather",
            description = "**" + question[0] + "**\n\n\n" + EMOJI_A + " " + question[1] + "\n\n" + EMOJI_B + " " + question[2],
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
