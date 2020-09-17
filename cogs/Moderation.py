import discord
from discord.ext import commands

from lib import libcassandra as cassandra

EMOJI_INFO = ":information_source:"
EMOJI_BAN = ":no_entry_sign:"
EMOJI_WARN = ":warning:"

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_help_page(self):
        return {
            "title": "Moderation Commands",
            "description": "These commands require moderation or administrator permissions.",
            "content": {
                "clear [count = 10]": "Clears the chat.",
                "ban <user> [reason...]": "Bans a user from the server.",
                "kick <user> [reason...]": "Kicks a user from the server.",
                "warn <user> [reason...]": "Warns a user.",
                # "history <user>": "Gets the moderation history for a user.",
                "whois <user>": "Displays some extended information about a user."
            }
        }

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member : discord.Member, *, reason = None):
        # Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            if reason is None:
                await caudit.print_audit(ctx.author, 'warning', "Warned %s#%s for no reason." % (member.name, member.discriminator))
            else:
                await caudit.print_audit(ctx.author, 'warning', "Warned %s#%s for **\"%s\"**." % (member.name, member.discriminator, reason))

        reason_str = reason
        if reason is None:
            reason_str = "No reason given"

        embed = discord.Embed(
            title = "%s %s: You have been warned!" % (EMOJI_WARN, ctx.guild.name),
            description = "Reason: %s" % reason_str,
            colour = discord.Colour.gold()
        )

        await member.send(embed=embed)

        usr = cassandra.get_user((guild.id, member.id))

        # Dispatch event
        cassandra.dispatch("mod-warning", {"dauthor":ctx.author,"reason":reason,"duser":member,"user":usr})

        # TODO: Append to user history
        # usr = load_user(ctx.guild.id, member.id)
        # histentry = {
        #     "type": "warning",
        #     "time": getts(),
        #     "by": ctx.author.id,
        #     "reason": reason
        # }
        # usr["history"].append(histentry)
        # save_user(usr)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        # TODO: Tempban

        # Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            if reason is None:
                await caudit.print_audit(ctx.author, 'ban', "Baned %s#%s for no reason." % (member.name, member.discriminator))
            else:
                await caudit.print_audit(ctx.author, 'ban', "Baned %s#%s for **\"%s\"**." % (member.name, member.discriminator, reason))

        if reason is None:
            reason = "No reason given"

        embed = discord.Embed(
            title = "%s %s: The BAN-HAMMER has spoken!" % (EMOJI_BAN, ctx.guild.name),
            description = "Reason: %s" % reason,
            colour = discord.Colour.red()
        )

        # We need to send the message first because discord does not let you send messages to users that have no servers in common
        await member.send(embed=embed)

        usr = cassandra.get_user((guild.id, member.id))

        # Dispatch event
        cassandra.dispatch("mod-ban", {"dauthor":ctx.author,"reason":reason,"duser":member,"user":usr})

        await member.ban(reason=reason)

        # TODO: User history
        # usr = load_user(ctx.guild.id, member.id)
        # histentry = {
        #     "type": "ban",
        #     "time": getts(),
        #     "by": ctx.author.id,
        #     "reason": reason
        # }
        # usr["history"].append(histentry)
        # save_user(usr)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason = None):

        # Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            if reason is None:
                await caudit.print_audit(ctx.author, 'kick', "Kicked %s#%s for no reason." % (member.name, member.discriminator))
            else:
                await caudit.print_audit(ctx.author, 'kick', "Kicked %s#%s for **\"%s\"**." % (member.name, member.discriminator, reason))

        if reason is None:
            reason = "No reason given"

        embed = discord.Embed(
            title = "%s %s: You have beed kicked!" % (EMOJI_INFO, ctx.guild.name),
            description = "Reason: %s" % reason,
            colour = discord.Colour.dark_orange()
        )

        # We need to send the message first because discord does not let you send messages to users that have no servers in common
        await member.send(embed=embed)

        usr = cassandra.get_user((guild.id, member.id))

        # Dispatch event
        cassandra.dispatch("mod-kick", {"dauthor":ctx.author,"reason":reason,"duser":member,"user":usr})

        await member.kick(reason=reason)

        # TODO: User history
        # usr = load_user(ctx.guild.id, member.id)
        # histentry = {
        #     "type": "kick",
        #     "time": getts(),
        #     "by": ctx.author.id,
        #     "reason": reason
        # }
        # usr["history"].append(histentry)
        # save_user(usr)

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

        # Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            await caudit.print_audit(ctx.author, 'clear', "Cleared %s messages from channel <#%s>" % (amt, ctx.channel.id))

        # Dispatch event
        cassandra.dispatch("mod-clear", {"dauthor":ctx.author,"amount":amt,"channel":ctx.channel})

def setup(client):
    client.add_cog(Moderation(client))
