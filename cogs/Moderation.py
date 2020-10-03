import discord
from discord.ext import commands
from discord.utils import get

from lib import libcassandra as cassandra
from lib.logging import Logger

EMOJI_INFO = ":information_source:"
EMOJI_BAN = ":no_entry_sign:"
EMOJI_WARN = ":warning:"

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._logger = Logger(self)

    def get_help_page(self):
        return {
            "title": "Moderation Commands",
            "description": "These commands require moderation or administrator permissions.",
            "content": {
                "clear [count = 10]": "Clears the chat.",
                "ban <user> [reason...]": "Bans a user from the server.",
                "kick <user> [reason...]": "Kicks a user from the server.",
                "warn <user> [reason...]": "Warns a user.",
                "quarantine <user> [reason...]": "Strips a user from all roles.",
                "unquarantine <user>": "Restores a users roles.",
                # "history <user>": "Gets the moderation history for a user.",
                "whois <user>": "Displays some extended information about a user."
            }
        }

    def is_user_quarantined(self, u):
        usr = cassandra.get_user(u)
        return usr.quarantine_status

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member : discord.Member, *, reason = None):
        self._logger.trace("warn")
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
        self._logger.trace("ban")
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


    @commands.command(name="qrole")
    @commands.has_permissions(manage_channels=True)
    async def qrole(self, ctx, action, role : discord.Role = None):
        self._logger.trace("qrole")

        srv = cassandra.get_server(ctx.guild.id)
        if action in ["unset", "remove", "delete", "del", "rem"]:
            srv.quarantine_role = None
            cassandra.save_server(srv)

            await ctx.send("Quarantine role unset.")

        elif action in ["set", "add"]:
            if role is None:
                return # TODO: Print help

            srv.quarantine_role = role.id
            cassandra.save_server(srv)

            await ctx.send("Quarantine role set.")

    @commands.command(name="quarantine")
    @commands.has_permissions(manage_roles=True)
    async def quarantine(self, ctx, member : discord.Member, *, reason = None):
        self._logger.trace("quarantine")

        usr = cassandra.get_user((ctx.guild.id, member.id))
        if usr.quarantine_status == True:
            await ctx.send("This user is already in quarantine!")
            return

        # Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            if reason is None:
                await caudit.print_audit(ctx.author, 'quarantine', "Quarantined %s#%s for no reason." % (member.name, member.discriminator))
            else:
                await caudit.print_audit(ctx.author, 'quarantine', "Quarantined %s#%s for **\"%s\"**." % (member.name, member.discriminator, reason))

        old_roles = [];
        for role in member.roles:
            if role == ctx.guild.default_role:
                continue
            old_roles.append(role.id)
            try:
                await member.remove_roles(role, reason="Quarantine")
            except Exception as ex:
                self._logger.warn("Failed to remove role %s from member %s: %s" % (role.name, member.name, ex))

        if usr.server.quarantine_role is not None:
            qrole = get(ctx.guild.roles, id=usr.server.quarantine_role)
            if qrole is not None:
                try:
                    await member.add_roles(qrole, reason="Quarantine")
                except Exception as ex:
                    self._logger.warn("Failed to add role %s to member %s: %s" % (qrole.name, member.name, ex))

        # Dispatch event
        cassandra.dispatch("mod-quarantine", {"dauthor":ctx.author,"reason":reason,"duser":member,"user":usr})

        usr.quarantine_status = True
        usr.quarantine_roles = old_roles
        cassandra.save_user(usr)

        await ctx.send("User %s#%s has been quarantined." % (member.name, member.discriminator))

    @commands.command(name="unquarantine")
    @commands.has_permissions(manage_roles=True)
    async def unquarantine(self, ctx, member : discord.Member):
        self._logger.trace("unquarantine")

        usr = cassandra.get_user((ctx.guild.id, member.id))
        if usr.quarantine_status == False:
            await ctx.send("This user is not in quarantine!")
            return

# Audit log
        caudit = self.client.get_cog('Audit')
        if caudit is not None:
            if reason is None:
                await caudit.print_audit(ctx.author, 'unquarantine', "Unquarantined %s#%s." % (member.name, member.discriminator))

        if usr.server.quarantine_role is not None:
            qrole = get(ctx.guild.roles, id=usr.server.quarantine_role)
            if qrole is not None:
                try:
                    await member.remove_roles(qrole, reason="Unquarantine")
                except Exception as ex:
                    self._logger.warn("Failed to remove role %s from member %s: %s" % (qrole.name, member.name, ex))

        for roleid in usr.quarantine_roles:
            role = get(ctx.guild.roles, id=roleid)
            if role is None:
                continue
            if role == ctx.guild.default_role:
                continue
            try:
                await member.add_roles(role, reason="Unquarantine")
            except Exception as ex:
                self._logger.warn("Failed to add role %s to member %s: %s" % (role.name, member.name, ex))

        # Dispatch event
        cassandra.dispatch("mod-unquarantine", {"dauthor":ctx.author,"duser":member,"user":usr})

        usr.quarantine_status = False
        usr.quarantine_roles = []
        cassandra.save_user(usr)

        await ctx.send("User %s#%s has been released form quarantine." % (member.name, member.discriminator))

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        self._logger.trace("kick")

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
        self._logger.trace("clear")
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
