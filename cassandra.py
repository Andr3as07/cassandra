# bot.py
import os
import json
import random
import time
import datetime
import math

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# ==============================================================================
# Config
# ==============================================================================

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '$'

NICKNAME_TIMEOUT=15*60

HELP_TIMEOUT = 20
RUSR_TIMEOUT = 5

EMOJI_FIRST = "⏮"
EMOJI_PREVIOUS = "◀"
EMOJI_NEXT = "▶"
EMOJI_LAST = "⏭"
EMOJI_CLOSE = "⏹"
EMOJI_JOIN = "🆗"
EMOJI_FIRE = "🔫"
EMOJI_ALIVE = "👥"
EMOJI_DEAD = "⚰"

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

def save_user(usr):
    path = get_user_path(usr['gid'], usr['uid'])

    os.makedirs(get_server_path(usr['gid']), exist_ok=True)

    with open(path, 'w') as f:
        json.dump(usr, f, indent=2, sort_keys=True)

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
        hmsg["time"] = getts()
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
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command(name="unload")
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')


@bot.command(name="reload")
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')

# General
bot.remove_command('help')

@bot.command(name="help", help="Shows the help menu.")
async def help(ctx):
    global help_pages

    # TODO: Update help pages
    if help_pages is None:
        help_pages = []
        for cogname in _get_loaded_cogs():
            try:
                page = bot.get_cog(cogname).get_help_page()
                help_pages.append(page)
            except:
                pass

    embed = get_help_page(0)

    msg = await ctx.send(embed=embed)

    help_messages[msg.id] = {
        "msg": msg,
        "gid": ctx.guild.id,
        "cid": ctx.channel.id,
        "time": getts(),
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

@bot.command(name="whois", help="Get's information about a user")
@commands.has_permissions(manage_messages=True)
async def whois(ctx, member : discord.Member):
    usr = load_user(ctx.guild.id, member.id, False)
    if usr is None:
        await ctx.send("Couldn't get user information")
        return

    title = member.name + "#" + member.discriminator
    if member.nick is not None:
        title = title + " (" + member.nick + ")"

    nicknames = "No nicknames tracked"
    if len(usr["nicknames"]) > 0:
        nicknames = "```" + ', '.join(usr['nicknames']) + '```'

    embed = discord.Embed(
        title = title
    )
    embed.set_thumbnail(url=member.avatar_url)

    embed.add_field(name="ID", value=str(member.id))
    embed.add_field(name="Account Created", value=str(member.created_at), inline=True)
    embed.add_field(name="Joined At", value=str(member.joined_at), inline=True)
    embed.add_field(name="Nicknames", value=nicknames)

    await ctx.send(embed=embed)

# Settings

@bot.command(name="settings", help="Allows the admin to configure the bot")
@commands.has_permissions(administrator=True)
async def settings(ctx, action = None, key = None, value = None):

    srv = load_server(ctx.guild.id)

    if action is None:
        await ctx.send("Usage: " + srv['prefix_used'] + "settings <set/get/add/remove> <key> [value]")
        return

    if action == "set":
        if key is None or value is None:
            resp = "You need to specify key and value."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nprefix\tSets the bot prefix for this server."
            await ctx.send(resp)
            return

        if key == "prefix":
            srv['prefix_used'] = str(value)
            await ctx.send("Prefix set to " + srv['prefix_used'])
            save_server(srv)
            return
        else:
            resp = "Invalid key " + key + "."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nprefix\tSets the bot prefix for this server."
            await ctx.send(resp)
            return

    elif action == "get":
        if key is None:
            resp = "You need to specify a key."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nprefix\tGets the current bot prefix for this server."
            resp = resp + "\nblocked\tGets the current list of blocked profixes."
            await ctx.send(resp)
            return

        if key == "prefix":
            await ctx.send("The current prefix is " + str(srv['prefix_used']))
            return

        elif key == "blocked":
            resp = "Blocked Prefixes: "
            resp = resp + ', '.join(srv['prefix_blocked'])
            await ctx.send(resp)
            return

        else:
            resp = "Invalid key " + key + "."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nprefix\tGets the current bot prefix for this server."
            resp = resp + "\nblocked\tGets the current list of blocked profixes."
            await ctx.send(resp)
            return

    elif action == "add":
        if key is None or value is None:
            resp = "You need to specify key and value."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nblocked\tAdds to the list of prefixes blocked on this server."
            await ctx.send(resp)
            return

        if key == "blocked":
            if str(value) in srv['prefix_blocked']:
                await ctx.send("This prefix is already blocked.")
                return

            srv['prefix_blocked'].append(str(value))
            save_server(srv)

            await ctx.send("Prefix " + str(value) + " is now blocked.")
            return

        else:
            resp = "Invalid key " + key + "."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nblocked\tAdds to the list of prefixes blocked on this server."
            await ctx.send(resp)
            return

    elif action == "remove":
        if key is None or value is None:
            resp = "You need to specify key and value."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nblocked\tRemoves from the list of prefixes blocked on this server."
            await ctx.send(resp)
            return

        if key == "blocked":
            if not str(value) in srv['prefix_blocked']:
                await ctx.send("This prefix is not blocked.")
                return

            srv['prefix_blocked'].remove(str(value))
            save_server(srv)

            await ctx.send("Prefix " + str(value) + " is no longer blocked.")
            return

        else:
            resp = "Invalid key " + key + "."
            resp = resp + "\n**Possible keys:**"
            resp = resp + "\nblocked\tRemoves from the list of prefixes blocked on this server."
            await ctx.send(resp)
            return
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

@tasks.loop(seconds=NICKNAME_TIMEOUT)
async def update_nicknames():
    print("Processing Nickname Changes")

    for guild in bot.guilds:
        # Do not do anything for unavailable guilds
        if guild.unavailable == True:
            continue

        for member in guild.members:
            if member.bot:
                continue

            if member.nick is not None:
                usr = load_user(guild.id, member.id)
                if not member.nick in usr['nicknames']:
                    usr['nicknames'].append(member.nick)
                    save_user(usr)

@tasks.loop(seconds=HELP_TIMEOUT)
async def update_help():
    if len(help_messages) == 0:
        return

    print("Processing Help Messages")

    for hmsgid in help_messages:
        hmsg = help_messages[hmsgid]
        print(getts() - hmsg["time"])
        if getts() - hmsg["time"] > 60:
            try:
                msg = hmsg["msg"]

                await msg.clear_reaction(EMOJI_FIRST)
                await msg.clear_reaction(EMOJI_PREVIOUS)
                await msg.clear_reaction(EMOJI_NEXT)
                await msg.clear_reaction(EMOJI_LAST)
            except Exception:
                print(ex)

            help_messages.pop(hmsgid)

def _get_loaded_cogs():
    cogs = []
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cogname = filename[:-3]
            cog = bot.get_cog(cogname)
            if cog is not None:
                cogs.append(cogname)

    return cogs

# Load add cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        print("Loading cog: %s" % filename)
        bot.load_extension("cogs.%s" % filename[:-3])

update_nicknames.start()
update_help.start()
print(f'Cassandra has connected to Discord!')

bot.run(TOKEN)
