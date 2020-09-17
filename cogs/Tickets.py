import discord
from discord.ext import commands
from discord.utils import get

from lib.data import Ticket
from lib import libcassandra as cassandra

class Tickets(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_help_page(self):
        return {
            "title": "Ticket Commands",
            "description": None,
            "content": {
                "ticket open <Topic>": "Opens a new ticket.",
                "ticket adduser": "Adds a user to a ticket.",
                "ticket remuser": "Removes a user from a ticket.",
                "ticket rename <New Topic>": "Changes the name of the ticket.",
                "ticket close": "Closes the ticket."
            }
        }

    async def open(self, dguild, duser, name):
        srv = cassandra.get_server(dguild.id)

        # Get category
        cat = get(dguild.categories, id=srv.tickets_category)
        if cat is None:
            return False, "Server not set up"

        # Configure Permissions
        perms = discord.PermissionOverwrite(read_messages=True)
        overwrites = {
            dguild.default_role: discord.PermissionOverwrite(read_messages=True), # @everyone
            dguild.me: perms, # Cassandra bot
            duser: perms # The creator of the ticket
        }

        # Admins
        for adminrole in srv.tickets_roles_admin:
            role = get(dguild.roles, id=adminrole)
            if role is None:
                continue
            overwrites[role] = perm

        # Moderators
        for modrole in srv.tickets_roles_moderator:
            role = get(dguild.roles, id=modrole)
            if role is None:
                continue
            overwrites[role] = perm

        # Find out the next ticket id
        id = srv.tickets_next_id
        srv.tickets_next_id = srv.tickets_next_id + 1

        chname = str("%s %s" % (id, name))

        # Create channel
        channel = await dguild.create_text_channel(chname, overwrites=overwrites, category=cat, reason="Ticket %s created by %s#%s" % (id, duser.name, duser.discriminator))

        # Create ticket object
        ticket = Ticket(srv, id, name, channel.id, False, [duser.id], "open")
        srv.tickets.append(ticket)

        cassandra.save_server(srv)

        # Send intial message
        embed = discord.Embed(
            title = "Welcome " + duser.name,
            description = "Please describe the reasoning for opening this ticket, include any information you think may be relevant such as proof, other third parties and so on.\n\nUse the following command to close the ticket\n `" + srv.prefix_used + "ticket close [reason for closing]`")

        await channel.send(embed=embed)

        # TODO: Send message to the ticket updates channel

        return True, ticket

    async def close(self, dguild, duser, channel):
        srv = cassandra.get_server(dguild.id)

        ticket = None
        for t in srv.tickets:
            if t.channel == channel.id:
                ticket = t
                break

        if ticket is None:
            return False, "This command can only be ran in an open ticket!"
            return

        # TODO: Save messages to text file and upload
        # What to do with images and other uploads? (Download + Zip)

        # Update ticket
        ticket.status = "closed"
        ticket.channel = None
        cassandra.save_server(srv)

        # Remove channel
        await channel.delete(reason="Ticket " + str(ticket.ID) + " closed by " + duser.name + "#" + str(duser.discriminator))

        return True, None

    def add_user(self, ticket, u):
        pass # Add a user to a ticket

    def rem_user(self, ticket, u):
        pass # Remove a user from a ticket

    def set_admin_only(self, ticket, ao):
        pass # Set or unset admin only status

    @commands.command(name="ticket")
    async def ticket(self, ctx, action=None, *, name=None):
        srv = cassandra.get_server(ctx.guild.id)

        if srv.tickets_channel_closed is None or srv.tickets_category is None:
            await ctx.send("The ticket system is not set up. Please contect an administrator.")
            return

        if action is None:
            # TODO: Print Help
            return

        elif action in ["create", "open", "new", "start", "add"]:
            if name is None:
                # TODO: Print Help
                return

            success, response = await self.open(ctx.guild, ctx.author, name)

            # TODO: Handle error

            # Send message to the calling channel
            await ctx.send("Ticket #" + str(response.ID) + " opened in <#" + str(response.channel) + ">")

            # TODO: Send message to the ticket updates channel
            return

        elif action in ["close", "end", "delete", "del", "remove", "rem", "rm"]:
            success, response = await self.close(ctx.guild, ctx.author, ctx.channel)

            # TODO: Handle error

            # TODO: Send message to the ticket updates channel
            return

        elif action in ["adminonly", "admin_only", "ao"]:
            await ctx.send("Not implemented!")
            return

        elif action in ["adduser", "add_user", "useradd", "au"]:
            await ctx.send("Not implemented!")
            return

        elif action in ["removeuser", "remove_user", "deleteuser", "delete_user", "deluser", "del_user", "userrem", "userdel", "ru", "du"]:
            await ctx.send("Not implemented!")
            return

        elif action in ["rename", "ren", "mv"]:
            await ctx.send("Not implemented!")
            return


def setup(client):
    client.add_cog(Tickets(client))
