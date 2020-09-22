import random
import time

import discord
from discord.ext import commands
from lib import util
from lib import libcassandra as cassandra
from lib.logging import Logger


EMOJI_WARN = "⚠"
EMOJI_ERROR = "❌"
EMOJI_MONEY = ":moneybag:"
IMAGE_TAILS = "https://i.imgur.com/i6XvztF.png"
IMAGE_HEADS = "https://i.imgur.com/BvnksIe.png"

class Cassino(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    def get_help_page(self):
        return {
            "title": "Casino Commands",
            "description": None,
            "content": {
                #"lottery": "Buy a lottery ticket.",
                "coinflip <heads|tails> [bet = 0]": "Flip a coin and bet on the outcome.",
                #"slots [bet = 0]": "Spin the slots for a chance to win the jackpot!",
                # "spin": "Spin the wheel every 5 minutes for a reward.",
                #"scratch": "Scratch a card for a chance to win a reward.",
                #"dice": Roll the dice, if you roll a 6 you'll get your bet x5!",
                # "snakeeyes": "Two dice are rolled. Roll a 1 on either one to win. Get both on 1 to recieve a special bonus reward.",
                # "blackjack": "Play a game of blackjack.",
            }
        }

    def _get_bet(self, bet):
        if bet is None:
            return 0

        if not bet.isdigit():
            return None

        # At this point the number can not be negative
        return int(bet)

    async def _can_afford(self, ctx, u, bet):
        cecon = self.client.get_cog('Economy')
        if cecon is None:
            await ctx.send(EMOJI_ERROR + " Betting for coins is not configured!")
            return False
        if not cecon.has_balance(u, bet):
            await ctx.send(EMOJI_ERROR + " You can't afford this bet!")
            return False

        return True

    async def _usage_coinflip(self, ctx):
        await ctx.send("Usage: $coinflip <heads|tails> [amt=0]")

    @commands.command(name="coinflip", help="Flip a coin and bet on the outcome.")
    async def coinflip(self, ctx, side = None, bet = None):
        self._logger.trace("coinflip")
        if side is None:
            await self._usage_coinflip(ctx)
            return

        bet = self._get_bet(bet)
        if bet is None:
            await self._usage_coinflip(ctx)
            return

        usr = None
        if bet > 0:
            usr = cassandra.get_user((ctx.guild.id, ctx.author.id))

            #  Check if the user of this command has that much money
            if not await self._can_afford(ctx, usr, bet):
                return

        rng_side = -1
        if side == "heads":
            rng_side = 0
        elif side == "tails":
            rng_side = 1
        else:
            await self._usage_coinflip(ctx)
            return

        flip = random.randint(0, 1)

        thumbnail = None
        flip_str = None
        if flip == 1:
            flip_str = "tails"
            thumbnail = IMAGE_TAILS
        else:
            flip_str = "heads"
            thumbnail = IMAGE_HEADS

        won = (flip == rng_side)

        color = None
        description = "It's **%s**\n" % flip_str

        if won:
            color = discord.Colour.green()
            description = description + "You won"
        else:
            color = discord.Colour.red()
            description = description + "You lost"

        if bet > 0:
            cecon = self.client.get_cog('Economy') # This can always be found because of the _can_afford check

            if won:
                cecon.add_balance(usr, bet)
            else:
                cecon.add_balance(usr, -bet)

            description = description + (" %s " % bet) + EMOJI_MONEY + ("\nYou now have %s " % usr.balance) + EMOJI_MONEY

        embed = discord.Embed(
            title = "Coinflip",
            colour = color,
            description = description
        )
        embed.set_thumbnail(url=thumbnail)

        await ctx.send(embed=embed)

        if usr:
            cassandra.save_user(usr)

    @commands.command(name="lottery")
    async def lottery(self, ctx):
        self._logger.trace("lottery")
        await ctx.send("Not implemented")

    @commands.command(name="slots")
    async def slots(self, ctx):
        self._logger.trace("slots")
        await ctx.send("Not implemented")

    @commands.command(name="scratch")
    async def scratch(self, ctx):
        self._logger.trace("scratch")
        await ctx.send("Not implemented")

    @commands.command(name="dice")
    async def dice(self, ctx):
        self._logger.trace("dice")
        await ctx.send("Not implemented")

    @commands.command(name="snakeeyes")
    async def snakeeyes(self, ctx):
        self._logger.trace("snakeeyes")
        await ctx.send("Not implemented")

    @commands.command(name="blackjack")
    async def blackjack(self, ctx):
        self._logger.trace("blackjack")
        await ctx.send("Not implemented")

    # Casino
    @commands.command(name="spin", help="Spin the wheel every 5 minutes for a reward.")
    async def spin(self, ctx):
        self._logger.trace("spin")
        ods = [
            { "symbol": "<:c500:710482148305403924>", "propbability": 1, "ods": 500, "name": "MYTHIC" },
            { "symbol": "<:c100:710482154500653056>", "propbability": 2, "ods": 100, "name": "IMORTAL" },
            { "symbol": "<:c50:710482156895469691>", "propbability": 4, "ods": 50, "name": "LEGENDARY" },
            { "symbol": "<:c25:710482155310022758>", "propbability": 8, "ods": 25, "name": "EPIC" },
            { "symbol": "<:c10:710482151484817439>", "propbability": 16, "ods": 10, "name": "RARE" },
            { "symbol": "<:c5:710482137895403520>", "propbability": 24, "ods": 5, "name": "UNCOMMON" },
            { "symbol": "<:c1:710482104705613845>", "propbability": 48, "ods": 1, "name": "COMMON" }
        ]

        usr = cassandra.get_user((ctx.guild.id, ctx.author.id))

        ts = util.getts()
        if ts - usr.casino_last_spin < 300:
            await ctx.send("You have to wait " + util.sec2human(300 - (ts - usr.casino_last_spin)) + " for your next chance of a reward.")
            return

        total = 0
        for outcome in ods:
            total = total + outcome["propbability"]

        rand = random.randint(0, total)
        index = 0
        out = None
        while rand > 0:
            outcome = ods[index]
            rand = rand - outcome["propbability"]

            if rand <= 0:
                out = outcome
                break
            index = index + 1

        # FIX: This is a drity fix, as we should never end up here
        if out is None:
            out = ods[0]

        embed = discord.Embed(
            title = ctx.author.display_name + " spins the wheel ...",
            description = "<a:spin:710491435006165032> | Spinning ...",
            colour = discord.Colour.green()
        )

        msg = await ctx.send(embed=embed)

        # FIX: Replace this with a timer, because this forces only one player (in al servers) to be able to spin at once
        time.sleep(1)

        description = "%s | Landed on **%s**" % (out["symbol"], out["name"])

        cecon = self.client.get_cog('Economy')
        if cecon is not None:
            description = description + ("\nYou got a reward of %s coins" % out["ods"])
            cecon.add_balance(usr, out["ods"])
        else:
            description = description + ("\n\n%s You did not get a reward, because the economy is not setup!" % EMOJI_WARN)

        embed = discord.Embed(
            title = ctx.author.display_name + " Spun the wheel",
            description = description,
            colour = discord.Colour.green()
        )

        await msg.edit(embed=embed)

        usr.casino_last_spin = ts
        cassandra.save_user(usr)

def setup(client):
    client.add_cog(Cassino(client))
