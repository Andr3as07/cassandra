import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amt = 10):
        if not type(amt) is int:
            try:
                amt = int(amt, 10)
            except ValueError:
                await ctx.send("Invalid number of messages given")
                return

        if amt < 1:
            await ctx.send("Can not remove %s messages" % amt)
            return
        elif amt > 100:
            amt = 100

        await ctx.channel.purge(limit=amt + 1)

        # TODO: Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            await caudit.print_audit(ctx.author, 'clear', "Cleared %s messages from channel <#%s>" % (amt, ctx.channel.id))

def setup(client):
    client.add_cog(Moderation(client))
