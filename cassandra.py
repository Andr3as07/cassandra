import os
import json
import random
import time
import datetime
import math
import requests

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from lib import util, data
from lib import libcassandra as cassandra

# ==============================================================================
# Config
# ==============================================================================

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
HEALTHCHECKS_TOKEN = os.getenv('HEALTHCHECKS_TOKEN')

HELP_TIMEOUT = 20
HEALTHCHECKS_TIMEOUT = 3600

EMOJI_FIRST = "⏮"
EMOJI_PREVIOUS = "◀"
EMOJI_NEXT = "▶"
EMOJI_LAST = "⏭"

# ==============================================================================
# Cache
# ==============================================================================
help_messages = {}

# ==============================================================================
# Util
# ==============================================================================

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

    srv = cassandra.get_server(message.guild)
    return srv.prefix_used

bot = commands.Bot(command_prefix=get_prefix)

# ==============================================================================
# Events
# ==============================================================================

async def handle_help_reaction(reaction, user):
    global help_messages
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

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot == True:
        return

    # Do not do anything on private messages
    if reaction.message.guild is None:
        return

    if reaction.message.id in help_messages:
        await handle_help_reaction(reaction, user)

# ==============================================================================
# Commands
# ==============================================================================

help_pages = None

# Debug
@bot.command(name="load")
@commands.has_permissions(administrator=True)
async def load(ctx, name):
    global help_pages

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

    # Dispatch preload event
    response = cassandra.dispatch("cog-loading", type('',(object,),{"name":name, "cancel":False})())

    if response.cancel == True:
        await ctx.send("Cog %s has been stoped form loading!" % name)
        return

    bot.load_extension("cogs.%s" % name)

    active_cogs.append(cog)
    help_pages = None # Clear help page cache

    # Dispatch event
    cassandra.dispatch("cog-loaded", type('',(object,),{"name":name})())

    await ctx.send("Cog %s loaded." % name)

@bot.command(name="unload")
@commands.has_permissions(administrator=True)
async def unload(ctx, name):
    global help_pages

    cog = None
    for c in active_cogs:
        if c.name == name:
            cog = c
            break

    if cog is None:
        await ctx.send("No active cog with name %s found!" % name)
        return

    # Dispatch preload event
    response = cassandra.dispatch("cog-unloading", type('',(object,),{"name":name, "cancel":False})())

    if response.cancel == True:
        await ctx.send("Cog %s has been stoped form unloading!" % name)
        return

    # TODO: Unregister all event handlers for this cog

    active_cogs.remove(cog)
    bot.unload_extension("cogs.%s" % name)
    help_pages = None # Clear help page cache

    # Dispatch event
    cassandra.dispatch("cog-unloaded", type('',(object,),{"name":name})())

    await ctx.send("Cog %s unloaded." % name)

@bot.command(name="reload")
@commands.has_permissions(administrator=True)
async def reload(ctx, name):
    global help_pages

    # TODO: Maybe we need to dispatch events here to

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
    else:
        active_cogs.append(cog)

    bot.load_extension("cogs.%s" % name)

    help_pages = None # Clear help page cache

    await ctx.send("Cog %s reloaded." % name)

# General
bot.remove_command('help')

@bot.command(name="help", help="Shows the help menu.")
async def help(ctx):
    global help_pages

    # TODO: Update help pages
    if help_pages is None:
        print("Creating help page cache")
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
# @bot.command(name="history", help="Displays a users moderation history.")
# async def history(ctx, member : discord.Member):
#     usr = load_user(ctx.guild.id, member.id, False)
#     if usr is None or len(usr['history']) == 0:
#         embed = discord.Embed(
#             title = member.name + "#" + member.discriminator,
#             description = "This user does not have a moderation history."
#         )
#         embed.set_thumbnail(url=member.avatar_url)

#         await ctx.send(embed=embed)
#         return

#     bans = 0
#     kicks = 0
#     warnings = 0

#     for entry in usr["history"]:
#         if entry["type"] == "warning":
#             warnings = warnings + 1
#         elif entry["type"] == "kick":
#             kicks = kicks + 1
#         elif entry["type"] == "ban":
#             bans = bans + 1

#     description = ""
#     for entry in usr["history"]:
#         if entry["type"] == "warning":
#             description = description + "\n:warning:"
#         elif entry["type"] == "ban":
#             description = description + "\n:no_entry_sign:"
#         elif entry["type"] == "kick":
#             description = description + "\n:information_source:"

#         description = description + " " + datetime.datetime.fromtimestamp(entry["time"]).strftime('%Y-%m-%d %H:%M:%S') + " | "

#         mod = bot.get_user(entry["by"])
#         if mod is not None:
#             description = description + "by **" + mod.name + "** "

#         if entry["reason"] is not None:
#             description = description + "reason: \"**" + entry["reason"] + "**\""

#     embed = discord.Embed(
#         title = member.name + "#" + member.discriminator,
#         description = description
#     )
#     embed.set_thumbnail(url=member.avatar_url)

#     embed.add_field(name=":no_entry_sign: Bans", value=str(bans), inline=True)
#     embed.add_field(name=":information_source: Kicks", value=str(kicks), inline=True)
#     embed.add_field(name=":warning: Warnings", value=str(warnings), inline=True)
#     await ctx.send(embed=embed)

# ==============================================================================
# Tasks
# ==============================================================================

@tasks.loop(seconds=HELP_TIMEOUT)
async def update_help():
    global help_messages
    if len(help_messages) == 0:
        return

    print("Processing Help Messages")

    new_help_messages = {}
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

        else:
            new_help_messages[hmsgid] = hmsg

    help_messages = new_help_messages

@tasks.loop(seconds=HEALTHCHECKS_TIMEOUT)
async def update_healthchecks():
    if HEALTHCHECKS_TOKEN is None:
        return

    print("Pinging healthchecks.io")

    try:
        requests.get("https://hc-ping.com/%s" % HEALTHCHECKS_TOKEN, timeout=10)
        print("Healthcheck successful")
    except requests.RequestException as e:
        print("Ping to healthchecks.io failed! %s" % e)

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
if HEALTHCHECKS_TOKEN is not None:
    update_healthchecks.start()

print("Cassandra has connected to Discord!")
print("Finished starting Cassandra Bot.")

bot.run(DISCORD_TOKEN)
