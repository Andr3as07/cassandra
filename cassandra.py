import os
import json
import random
import time
import datetime
import math

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from lib import util, data

# ==============================================================================
# Config
# ==============================================================================

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

HELP_TIMEOUT = 20

EMOJI_FIRST = "⏮"
EMOJI_PREVIOUS = "◀"
EMOJI_NEXT = "▶"
EMOJI_LAST = "⏭"
EMOJI_CLOSE = "⏹"
EMOJI_JOIN = "🆗"

# ==============================================================================
# Cache
# ==============================================================================
help_messages = {}

# ==============================================================================
# Util
# ==============================================================================

def get_server_path(gid):
    return "data/" + str(gid)

def get_user_path(gid, uid):
    return get_server_path(gid) + "/" + str(uid) + ".json"

def save_server(srv):
    path = get_server_path(srv['gid']) + "/config.json"

    os.makedirs(get_server_path(srv['gid']), exist_ok=True)

    with open(path, 'w') as f:
        json.dump(srv, f, indent=2, sort_keys=True)

def load_server(gid, create = True):
    path = get_server_path(gid) + "/config.json"

    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    else:
        if create == False:
            return None

        return {
            'gid': gid,
            'prefix_used': '$',
            'prefix_blocked': [],
            'audit_log': {
                'channel': None,
                'clear': True,
                'warn': True,
                'kick': True,
                'block': True
            },
            'roles_admin': [],
            'roles_mod': [],
            'tickets': {
                'channel_updates': None,
                'channel_closed': None,
                'next': 1,
                'list': {}
            }
        }

def load_user(gid, uid, create = True):
    path = get_user_path(gid, uid)

    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    else:
        if create == False:
            return None

        return {
            'gid': gid,
            'uid': uid,
            'coins': 0,
            'xp': 0,
            'msg': {
                'last': 0,
                'awarded': 0,
                'count': 0
            },
            'reaction': {
                'last': 0,
                'awarded': 0,
                'count': 0
            },
            'voice': {
                'time': 0
            },
            'history': [],
            'nicknames': [],
            'casino': {
                'last_spin': 0
            }
        }

def get_help_page(index):
    page = help_pages[index]
    embed = discord.Embed(
        title = page["title"],
        description = page["description"]
    )
    embed.set_author(name="Page " + str(index + 1) + "/" + str(len(help_pages)))
    for key in page["content"]:
        embed.add_field(name=key, value=page["content"][key], inline=False)

    return embed

def get_prefix(client, message):
    # Do not do anything on private messages
    if message.guild == None:
        return str(random.randrange(-99999999, 99999999))

    srv = bot.get_cog('Main').load_server(message.guild.id)
    return srv.prefix_used

bot = commands.Bot(command_prefix=get_prefix)

# ==============================================================================
# Events
# ==============================================================================

async def handle_help_reaction(reaction, user):
    hmsg = help_messages[reaction.message.id]

    if hmsg["uid"] != user.id:
        await reaction.remove(user)

    emoji = reaction.emoji
    done_something = False
    embed = None
    page_index = hmsg["page"]
    page = help_pages[page_index]
    if emoji == EMOJI_FIRST:
        done_something = True
        if hmsg["page"] > 0:
            page_index = 0
    elif emoji == EMOJI_PREVIOUS:
        done_something = True
        if hmsg["page"] > 0:
            page_index =  page_index - 1
    elif emoji == EMOJI_NEXT:
        done_something = True
        if hmsg["page"] < len(help_pages) - 1:
            page_index = page_index + 1
    elif emoji == EMOJI_LAST:
        done_something = True
        if hmsg["page"] < len(help_pages) - 1:
            page_index = len(help_pages) - 1

    if done_something:
        embed = get_help_page(page_index)

        hmsg["page"] = page_index
        hmsg["time"] = util.getts()
        help_messages[reaction.message.id] = hmsg

        await reaction.remove(user)

    if embed is not None:
        await reaction.message.edit(embed=embed)

# ==============================================================================
# Commands
# ==============================================================================

help_pages = None

help_pages_old = [
    {
        "title": "General Commands",
        "description": None,
        "content": {
            "help": "Shows this help dialog.",
            "profile  [user]": "Shows a users profile."
        }
    },
    {
        "title": "Ticket Commands",
        "description": "These commands may only work on servers which have configured the ticket system.",
        "content": {
            "ticket open/create/add <Topic>": "Opens a new ticket.",
            #"ticket addUser <User>": "Adds a user to the ticket.",
            #"ticket remUser/removeUser <User>": "Removes a user from the ticket.",
            #"ticket rename <Topic>": "Renames the ticket.",
            "ticket close/end/delete": "Closes the ticket."
        }
    },
    {
        "title": "Moderation Commands",
        "description": "These commands require moderation or administrator permissions.",
        "content": {
            "clear [count = 10]": "Clears the chat.",
            "ban <user> [reason...]": "Bans a user from the server.",
            "kick <user> [reason...]": "Kicks a user from the server.",
            "warn <user> [reason...]": "Warns a user.",
            "history <user>": "Gets the moderation history for a user.",
            "whois <user>": "Displays some extended information about a user."
        }
    }
]

# Debug
@bot.command(name="load")
@commands.has_permissions(administrator=True)
async def load(ctx, name):
    cog = None

    for cogname in cfg.cogs:
        if cogname == name:
            cog = cfg.cogs[cogname]
            break

    if cog is None:
        await ctx.send("No cog with name %s found!" % name)
        return

    if cog in active_cogs:
        await ctx.send("Cog %s is already loaded! You may want to use Reload!" % name)
        return

    bot.load_extension("cogs.%s" % name)

    active_cogs.append(cog)

    await ctx.send("Cog %s loaded." % name)

@bot.command(name="unload")
@commands.has_permissions(administrator=True)
async def unload(ctx, name):
    cog = None
    for c in active_cogs:
        if c.name == name:
            cog = c
            break

    if cog is None:
        await ctx.send("No active cog with name %s found!" % name)
        return

    active_cogs.remove(cog)
    bot.unload_extension("cogs.%s" % name)

    await ctx.send("Cog %s unloaded." % name)

@bot.command(name="reload")
@commands.has_permissions(administrator=True)
async def reload(ctx, name):
    cog = None

    for cogname in cfg.cogs:
        if cogname == name:
            cog = cfg.cogs[cogname]
            break

    if cog is None:
        await ctx.send("No cog with name %s found!" % name)
        return

    if cog in active_cogs:
        bot.unload_extension("cogs.%s" % name)

    bot.load_extension("cogs.%s" % name)

    active_cogs.append(cog)

    await ctx.send("Cog %s reloaded." % name)

# General
bot.remove_command('help')

@bot.command(name="help", help="Shows the help menu.")
async def help(ctx):
    global help_pages

    # TODO: Update help pages
    if help_pages is None:
        help_pages = []
        for cog in active_cogs:
            try:
                page = bot.get_cog(cog.name).get_help_page()
                help_pages.append(page)
            except:
                pass

    if len(help_pages) < 1:
        await ctx.send("Failed to display help pages.")
        return

    embed = get_help_page(0)

    msg = await ctx.send(embed=embed)

    help_messages[msg.id] = {
        "msg": msg,
        "gid": ctx.guild.id,
        "cid": ctx.channel.id,
        "time": util.getts(),
        "page": 0,
        "uid": ctx.author.id
    }

    await msg.add_reaction(EMOJI_FIRST)
    await msg.add_reaction(EMOJI_PREVIOUS)
    await msg.add_reaction(EMOJI_NEXT)
    await msg.add_reaction(EMOJI_LAST)

# Moderation
@bot.command(name="history", help="Displays a users moderation history.")
async def history(ctx, member : discord.Member):
    usr = load_user(ctx.guild.id, member.id, False)
    if usr is None or len(usr['history']) == 0:
        embed = discord.Embed(
            title = member.name + "#" + member.discriminator,
            description = "This user does not have a moderation history."
        )
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)
        return

    bans = 0
    kicks = 0
    warnings = 0

    for entry in usr["history"]:
        if entry["type"] == "warning":
            warnings = warnings + 1
        elif entry["type"] == "kick":
            kicks = kicks + 1
        elif entry["type"] == "ban":
            bans = bans + 1

    description = ""
    for entry in usr["history"]:
        if entry["type"] == "warning":
            description = description + "\n:warning:"
        elif entry["type"] == "ban":
            description = description + "\n:no_entry_sign:"
        elif entry["type"] == "kick":
            description = description + "\n:information_source:"

        description = description + " " + datetime.datetime.fromtimestamp(entry["time"]).strftime('%Y-%m-%d %H:%M:%S') + " | "

        mod = bot.get_user(entry["by"])
        if mod is not None:
            description = description + "by **" + mod.name + "** "

        if entry["reason"] is not None:
            description = description + "reason: \"**" + entry["reason"] + "**\""

    embed = discord.Embed(
        title = member.name + "#" + member.discriminator,
        description = description
    )
    embed.set_thumbnail(url=member.avatar_url)

    embed.add_field(name=":no_entry_sign: Bans", value=str(bans), inline=True)
    embed.add_field(name=":information_source: Kicks", value=str(kicks), inline=True)
    embed.add_field(name=":warning: Warnings", value=str(warnings), inline=True)
    await ctx.send(embed=embed)

# Tickets
@bot.command(name="ticket_old", help="Manages tickets")
async def ticket_old(ctx, action = None, *, name = None):
    srv = load_server(ctx.guild.id)

    if srv['tickets']['channel_closed'] is None or srv['tickets']['category'] is None:
        await ctx.send("The ticket system is not set up. Please contact an administrator.")
        return

    if action is None:
        # TODO: Print Help
        return
    elif action == "create" or action == "open" or action == "new" or action == "start":
        if name is None:
            # TODO: Print Help
            return

        # Get Category
        cat = None
        for c in ctx.guild.categories:
            if c.id == srv['tickets']['category']:
                cat = c
                break

        if cat is None:
            await ctx.send("The ticket channel is not set up. Please contact an administrator.")
            return

        # Configure Permissions
        perms = discord.PermissionOverwrite(read_messages=True)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: perms,
            ctx.author: perms
        }

        for admin in srv['roles_admin']:
            role = ctx.guild.get_role(admin)
            if role is None:
                continue
            overwrites[role] = perms

        for mod in srv['roles_mod']:
            role = ctx.guild.get_role(mod)
            if role is None:
                continue
            overwrites[role] = perms

        # Get id
        id = srv['tickets']['next']
        srv['tickets']['next'] = id + 1

        chname = str(id) + " " + name

        # Create Channel
        channel = await ctx.guild.create_text_channel(chname, overwrites=overwrites, category=cat, reason="Ticket " + str(id) + " created by " + ctx.author.name + "#" + str(ctx.author.discriminator))

        # Add to ticket list
        entry = {
            "id": id,
            "name": name,
            "channel": channel.id,
            "admin_only": False,
            "users": [
                ctx.author.id
            ],
            "status": "open"
        }
        srv['tickets']['list'][str(id)] = entry
        save_server(srv)

        # Send intial message
        embed = discord.Embed(
            title = "Welcome " + ctx.author.name,
            description = "Please describe the reasoning for opening this ticket, include any information you think may be relevant such as proof, other third parties and so on.\n\nuse the following command to close the ticket\n `" + srv['prefix_used'] + "ticket close [reason for closing]`"
        )

        # Send message to the calling channel
        await ctx.send("Ticket #" + str(id) + " opened in <#" + str(channel.id) + ">")

        await channel.send(embed=embed)

        # TODO: Send message to the ticket updates channel

    elif action == "close" or action == "end" or action == "delete" or action == "del":
        ch = ctx.channel

        ticket = None
        srv = load_server(ctx.guild.id)

        for sid in srv['tickets']['list']:
            entry = srv['tickets']['list'][sid]

            if entry['channel'] == ch.id:
                ticket = entry
                break

        if ticket is None:
            await ctx.send("This command can only be ran in an open ticket.")
            return

        # TODO: Save messages to text file
        # What to do with images and other uploads?

        # TODO: Upload text file

        # Update Ticket data
        ticket['status'] = "closed"
        ticket['channel'] = None
        srv['tickets']['list'][str(ticket['id'])] = ticket
        save_server(srv)

        # Remove Channel
        await ch.delete(reason="Ticket " + str(ticket['id']) + " closed by " + ctx.author.name + "#" + str(ctx.author.discriminator))

        # TODO: Send message to the ticket updates channel

# ==============================================================================
# Tasks
# ==============================================================================

@tasks.loop(seconds=HELP_TIMEOUT)
async def update_help():
    if len(help_messages) == 0:
        return

    print("Processing Help Messages")

    for hmsgid in help_messages:
        hmsg = help_messages[hmsgid]
        print(util.getts() - hmsg["time"])
        if util.getts() - hmsg["time"] > 60:
            try:
                msg = hmsg["msg"]

                await msg.clear_reaction(EMOJI_FIRST)
                await msg.clear_reaction(EMOJI_PREVIOUS)
                await msg.clear_reaction(EMOJI_NEXT)
                await msg.clear_reaction(EMOJI_LAST)
            except Exception:
                print(ex)

            help_messages.pop(hmsgid)

print("Starting Cassandra Bot...")

# Load config
print("Loading global bot configuration...")
cfg = data.CassandraConfig("data/config.json")
cfg.load()
print("Finished loading global bot configuration.")

print("Initializing autoload cogs...")
active_cogs = []
for cogname in cfg.cogs:
    cog = cfg.cogs[cogname]
    if cog.autoload == True:
        print("Autoloading cog: %s" % cog.name)
        bot.load_extension("cogs.%s" % cog.name)
        active_cogs.append(cog)
print("Finished initializing autoload cogs.")

update_help.start()
print(f'Cassandra has connected to Discord!')
print("Finished starting Cassandra Bot.")

bot.run(TOKEN)
