import discord
from discord.ext import commands
from discord.utils import get

class RoleCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online.')

    async def _print_roles(self, ctx, srv, title = "Here is a list of available roles"):
        # Print all roles on the server
        if len(srv.role_commands) == 0:
            await ctx.send("No role commands found")
            return

        text = "%s:\n" % title
        for group in srv.role_commands:
            text = text + ("\n**%s**\n" % group.name)
            if len(group.roles) > 0:
                text = text + ("```%s```\n" % str(group.roles)[1:-1])
            else:
                text = text + "No roles in this group.\n"

        await ctx.send(text)

    def _get_role(self, srv, name):
        if srv.role_commands == 0:
            return None, None

        for group in srv.role_commands:
            for role in group.roles:
                if role.name == name:
                    return group, role

        return None, None

    @commands.command(name="role")
    async def role(self, ctx, role = None):
        srv = self.client.get_cog('Main').load_server(ctx.guild.id)
        if role is None:
            # Print all roles on the server
            await self._print_roles(ctx, srv)
            return

        group, role = self._get_role(srv, role)
        if group is None or role is None:
            await self._print_roles(ctx, srv, "Role not found, here is a list of available roles")
            return

        drole = get(ctx.guild.roles, id=role.role)

        has_role = drole in ctx.author.roles

        # TODO: Check if the role could be found

        # TODO: Check group requirements

        # Check group type restrictions
        if group.mode != "none":
            # Get other roles in this group
            fgroles = []
            fdroles = []
            for urole in ctx.author.roles:
                for grole in group.roles:
                    if urole.id == grole.role:
                        fgroles.append(grole)
                        fdroles.append(urole)
                        break

            if group.mode == "single" and len(fgroles) > 0:
                if group.autoremove == True:
                    for fdrole in fdroles:
                        await ctx.author.remove_roles(fdrole, reason="Role command")
                        if fdrole != drole:
                            await ctx.send("Took away your %s role!" % fdrole.name)
                elif not has_role:
                    await ctx.send("Can not give you this role, because you have %s other role in this group!" % len(fgroles))
                    return
            elif group.mode == "multiple":
                if group.max is not None and group.max > 0 and len(fgroles) >= group.max and not has_role:
                    await ctx.send("Can not give you this role, because you have %s other role in this group!" % len(fgroles))
                    return

        # Toggle role
        if has_role:
            await ctx.author.remove_roles(drole, reason="Role command")
            await ctx.send("Took away your %s role!" % drole.name)
        else:
            await ctx.author.add_roles(drole, reason="Role command")
            await ctx.send("Gave you the %s role!" % drole.name)

        # TODO: Set timer to handle timelimit

def setup(client):
    client.add_cog(RoleCommands(client))
