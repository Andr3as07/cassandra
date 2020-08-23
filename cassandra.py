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

MSG_TIMEOUT = 60
MSG_BONUS_COINS = 1
MSG_BONUS_XP = 5

REACTION_TIMEOUT = 60
REACTION_BONUS_COINS = 1
REACTION_BONUS_XP = 1

VOICE_TIMEOUT = 5 * 60
VOICE_BONUS_COINS = 1
VOICE_BONUS_XP = 2

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

WYR_QUESTIONS = [
    ["Would you rather Swim 300 meters through shit or dead bodies?", "Swim 300 meters through shit", "Swim 300 meters through dead bodies"],
    ["Would you rather Have a dog with a cat’s personality or a cat with a dog’s personality?", "Have a dog with a cat’s personality", "Have a cat with a dog’s personality"],
    ["If you were reborn in a new life, would you rather be alive in the past or future?", "Be alive in the past", "Be alive in the future"],
    ["Would you rather eat no candy at Halloween or no turkey at Thanksgiving?", "Eat no candy at Halloween", "Eat no turkey at Thanksgiving"],
    ["Would you rather date someone you love or date someone who loves you?", "Date someone you love", "Date someone who loves you"],
    ["Would you rather lose the ability to lie or believe everything you’re told?", "Lose the ability to lie", "Believe everything you’re told"],
    ["Would you rather be free or be totally safe?", "Be free", "Be totally safe"],
    ["Would you rather Eat shit that tasted like chocolate, or eat chocolate that tasted like crap?", "Eat shit that tasted like chocolate", "Eat chocolate that tasted like crap"],
    ["Would you rather Look 10 years older from the neck up, or the neck down?", "Look 10 years older from the neck up", "Would you rather Look 10 years older from the neck down"],
    ["Would you rather Be extremely underweight or extremely overweight?", "Be extremely underweight", "Be extremely overweight"],
    ["Would you rather Experience the beginning of planet earth or the end of planet earth?", "Experience the beginning of planet earth", "Experience the end of planet earth"],
    ["Would you rather have three kids and no money, or no kids with three million dollars?", "Have three kids and no money", "No kids with three million dollars"],
    ["Would you rather Be the funniest person in the room or the most intelligent?", "Be the funniest person in the room", "Be the most intelligent person in the room"],
    ["Would you rather Have a Lamborghini in your garage or a bookcase with 9000 books and infinite knowledge?", "Have a Lamborghini in your garage", "Have a bookcase with 9000 books and infinite knowledge"],
    ["Would you rather Reverse one decision you make every day or be able to stop time for 10 seconds every day?", "Reverse one decision you make every day", "Be able to stop time for 10 seconds every day"],
    ["Would you rather Win $50,000 or let your best friend win $500,000?", "Win $50,000", "Let your best friend win $500,000"],
    ["Would you rather Run at 100 mph or fly at ten mph?", "Run at 100 mph", "Fly at ten mph"],
    ["Would you rather Continue with your life or restart it?", "Continue with your life", "Restart it"],
    ["Would you rather Be able to talk your way out of any situation, or punch your way out of any situation?", "Be able to talk your way out of any situation", "Be able to punch your way out of any situation"],
    ["Would you rather Have free Wi-Fi wherever you go or have free coffee where/whenever you want?", "Have free Wi-Fi wherever you go", "Have free coffee where/whenever you want"],
    ["Would you rather have seven fingers on each hand or have seven toes on each foot?", "Have seven fingers on each hand", "Have seven toes on each foot"],
    ["Would you rather live low life with your loved one or rich life all alone?", "Live low life with your loved one", "Rich life all alone"],
    ["Would you rather Have no one to show up for your Wedding or your funeral?", "Have no one to show up for your Wedding", "Have no one to show up for your funeral"],
    ["Would you rather Rule the World or live in a World with absolutely no problems at all?", "Rule the World", "Live in a World with absolutely no problems at all"],
    ["Would you rather go back to the past and meet your loved ones who passed away or go to the future to meet your children or grandchildren to be?", "Go back to the past and meet your loved ones who passed away", "Go to the future to meet your children or grandchildren to be"],
    ["Would you rather Speak your mind or never speak again?", "Speak your mind", "Never speak again"],
    ["Would you rather Live the life of a king with no family or friends or live like a vagabond with your friends or family?", "Live the life of a king with no family", "Live like a vagabond with your friends or family"],
    ["Would you rather know how you will die or when you will die?", "Know how you will die", "Know when you will die"],
    ["Would you rather Speak all languages or be able to speak to all animals?", "Speak all languages", "Be able to speak to all animals"],
    ["Would you rather get away with lying every time or always know that someone is lying?", "Get away with lying every time", "Always know that someone is lying"],
    ["Would you rather Eat your dead friend or kill your dog and eat it when you are marooned on a lonely island?", "Eat your dead friend", "Kill your dog and eat it"],
    ["Would you rather Have a billion dollars to your name or spend $1000 for each hungry and homeless person?", "Have a billion dollars to your name", "Spend $1000 for each hungry and homeless person"],
    ["Would you rather End death due to car accidents or end terrorism?", "End death due to car accidents", "End terrorism"],
    ["Would you rather Leave your unemployed son homeless or pay for his dr#g habits and illegal activities?", "Leave your unemployed son homeless", "Pay for his drug habits and illegal activities"],
    ["Would you rather End the life a single human being or 100 cute baby animals?", "End the life a single human", "End the life of 100 cute baby animals"],
    ["Would you rather Skinny dip with your classmate or with a stranger?", "Skinny dip with your classmate", "With a stranger"],
    ["Would you rather give up your love life or work life?", "Give up your love life", "Give up your work life"],
    ["Would you rather live in an amusement park or a zoo?", "Live in an amusement park", "Live in a zoo"],
    ["Would you rather be a millionaire by winning the lottery or by working 100 hours a week?", "Be a millionaire by winning the lottery", "Be a millionaire by working 100 hours a week"],
    ["Would you rather read minds or accurately predict future?", "Read minds", "Accurately predict future"],
    ["Would you rather eat only pizza for 1 year or eat no pizza for 1 year?", "Eat only pizza for 1 year", "Eat no pizza for 1 year"],
    ["Would you rather visit 100 years in the past or 100 years in the future?", "Visit 100 years in the past", "Visit 100 years in the future"]
]

# ==============================================================================
# Cache
# ==============================================================================
help_messages = {}
rusr_messages = {}

# ==============================================================================
# Util
# ==============================================================================

def sec2human(sec):
    hours = sec // (60 * 60)
    sec = sec % (60 * 60)

    m = sec // 60
    sec = sec % 60

    if hours > 0:
        return str(hours) + "h " + str(m) + "min "
    elif m > 0:
        return str(m) + "min " + str(sec) + "sec"
    else:
        return str(sec) + "sec"

def getts():
    return int(time.time())

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

def get_level(usr):
    lv = 1
    for i in range(2, 100):
        req = math.floor(math.pow(i, 3))
        if req < usr['xp']:
            lv = i
        else:
            break

    return lv

async def print_audit(gid, audit, uid, message):
    if gid is None:
        return

    srv = load_server(gid)
    if srv is None:
        return

    # If an "audit log" is enabled
    if srv['audit_log']['channel'] is not None and srv['audit_log'][audit] == True:
        ch = bot.get_channel(srv['audit_log']['channel'])
        if ch is not None:
            await ch.send("<@!" + str(uid) + ">: " + str(message))

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

def get_rusr_fields(rusr, embed):
    if len(rusr["alive"]) > 1:
        s = ""
        for u in rusr["alive"]:
            s = s + "<@" + str(u) + ">\n"
        embed.add_field(name=":busts_in_silhouette: Active Players", value=s, inline=True)

    s = ""
    for u in rusr["dead"]:
        s = s + "<@" + str(u) + ">\n"
    embed.add_field(name=":skull: Graveyard", value=s, inline=True)

    return embed

def get_prefix(client, message):
    # Do not do anything on private messages
    if message.guild == None:
        return str(random.randrange(-99999999, 99999999))

    srv = load_server(message.guild.id)
    return srv['prefix_used']

bot = commands.Bot(command_prefix=get_prefix)

# ==============================================================================
# Events
# ==============================================================================

@bot.event
async def on_message(message):
    print(message.content)
    if message.author.bot == True:
        return

    # Do not do anything on private messages
    if message.guild == None:
        return

    srv = load_server(message.guild.id)

    # Check if the message was a command from a player
    if not message.content.startswith(srv['prefix_used']):

        # If the message is a command for another bot. Do not do anything
        for pre in srv['prefix_blocked']:
            if message.content.startswith(pre):
                return

        usr = load_user(message.guild.id, message.author.id)
        usr['name'] = message.author.name
        usr['msg']['last'] = getts()

        # if msg timeout is reached award coins
        if getts() - usr['msg']['awarded'] > MSG_TIMEOUT:
            usr['msg']['awarded'] = getts()
            usr['coins'] = usr['coins'] + MSG_BONUS_COINS
            usr['xp'] = usr['xp'] + MSG_BONUS_XP

        usr['msg']['count'] = usr['msg']['count'] + 1
        save_user(usr)

    # Continue command handling
    await bot.process_commands(message)

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

async def handle_rusr_reaction(reaction, user, game):
    game_id = str(game["guild"].id) + ":" + str(game["channel"].id)
    if game["state"] == "setup":
        if reaction.emoji != EMOJI_JOIN:
            await reaction.remove(user)
            return

        if user.id in game["alive"]:
            await reaction.message.channel.send(content="<@" + str(user.id) + "> You are already in the game.", delete_after=5)
            return

        game["alive"].append(user.id)
        await reaction.message.channel.send("<@" + str(user.id) + "> Joined the game.", delete_after=5)
        rusr_messages[game_id] = game

    elif game["state"] == "running":
        print("Running")
        if reaction.emoji != EMOJI_FIRE:
            await reaction.remove(user)
            return
        if not user.id == game["alive"][game["index"]]:
            await reaction.remove(user)
            return

        kill = random.randint(0, 6)
        if kill == 0:
            # Kill
            pass
        else:
            # Alive

            embed = discord.Embed(
                title = "Russian Roulette",
                description = "<@" + str(game["alive"][game["index"]]) + "> lives to see another day..."
            )
            # TODO: Add alive
            # TODO: Add dead

            game["index"] = game["index"] + 1

        game["index"] = game["index"] % len(game["alive"])

        rusr_messages[game_id] = game

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot == True:
        return

    # Do not do anything on private messages
    if reaction.message.guild == None:
        return

    if reaction.message.id in help_messages:
        await handle_help_reaction(reaction, user)

    rusr_id = str(reaction.message.guild.id) + ":" + str(reaction.message.channel.id)
    if rusr_id in rusr_messages:
        rusr = rusr_messages[rusr_id]
        if rusr["msg"].id == reaction.message.id:
            await handle_rusr_reaction(reaction, user, rusr)

    # Do not count reactions to bots
    if reaction.message.author.bot == True:
        return

    usr = load_user(reaction.message.guild.id, user.id)
    usr['name'] = user.name
    usr['msg']['last'] = getts()

    # if msg timeout is reached award coins
    if getts() - usr['reaction']['awarded'] > REACTION_TIMEOUT:
        usr['reaction']['awarded'] = getts()
        usr['coins'] = usr['coins'] + REACTION_BONUS_COINS
        usr['xp'] = usr['xp'] + REACTION_BONUS_XP

    usr['reaction']['count'] = usr['reaction']['count'] + 1
    save_user(usr)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Missing Permissions")
    else:
        await ctx.send("Error while executing the command.")
        print(str(type(error)) + ": " + str(error))

# ==============================================================================
# Commands
# ==============================================================================

help_pages = [
    {
        "title": "General Commands",
        "description": None,
        "content": {
            "help": "Shows this help dialog.",
            "profile  [user]": "Shows a users profile."
        }
    },
    {
        "title": "Fun Commands",
        "description": None,
        "content": {
            "8ball <Question ...>": "Ask the magic 8ball.",
            #"conn <User>": "Starts a game of connect-4 against the mentioned user.",
            #"fortune": "Opens a fortune cookie.",
            #"rusr": "Plays a round of russian roulette.",
            #"tord": "Play a game of truth or dare.",
            #"ttt <User>": "Starts a game of Tick-Tack-Toe.",
            "wyr": "Displays a would you rather question.",
        }
    },
    {
        "title": "Casino Commands",
        "description": None,
        "content": {
            #"lottery": "Buy a lottery ticket.",
            #"coinflip <heads|tails> [bet = 0]": "Flip a coin and bet on the outcome.",
            #"slots [bet = 0]": "Spin the slots for a chance to win the jackpot!",
            "spin": "Spin the wheel every 5 minutes for a reward.",
            #"scratch": "Scratch a card for a chanceto win a reward."
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

# General
bot.remove_command('help')

@bot.command(name="help", help="Shows the help menu.")
async def help(ctx):
    page = help_pages[0]
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

@bot.command(name="profile", help="Shows the profile.")
async def profile(ctx, name = None):
    # Do not do anything on private messages
    if ctx.guild == None:
        return

    uid = ctx.author.id
    if not name == None:
        if name.startswith("<@!") and name.endswith(">"):
            uid = name[3:len(name) - 1]

    usr = load_user(ctx.guild.id, uid, False)
    if usr == None:
        await ctx.send("User not found.")
        return

    discord_user = bot.get_user(usr['uid'])

    if discord_user is None:
        await ctx.send("User not found.")
        return

    content =          ":moneybag: Coins: " + str(usr['coins'])
    content = content +  "\n:star: XP:    " + str(usr['xp'])
    content = content + "\n:star2: Level: " + str(get_level(usr))

    embed = discord.Embed(
        title = "Profile for " + usr["name"] + " on server " + ctx.guild.name,
        description = content,
        colour = discord.Colour.green()
    )
    embed.set_thumbnail(url=discord_user.avatar_url)

    embed.add_field(name=":writing_hand: Messages", value="Total: " + str(usr['msg']['count']), inline=True)
    embed.add_field(name=":heart: Reactions", value="Total: " + str(usr['reaction']['count']), inline=True)
    embed.add_field(name=":microphone2: Voice", value="Time: " + sec2human(usr['voice']['time']), inline=True)

    await ctx.send(embed=embed)

# Fun
@bot.command(name="rusr", help="Plays a round of russian roulette")
async def rusr(ctx):
    id = str(ctx.guild.id) + ":" + str(ctx.channel.id)

    if id in rusr_messages:
        await ctx.send("A russian roulette is already in progress in this channel.")
        return

    msg = await ctx.send("<@" + str(ctx.author.id) + "> has initiated a game of RussianRoulette in this channel!\nReact with " + EMOJI_JOIN +" to join. You have 20.0 seconds to participate.")

    await msg.add_reaction(EMOJI_JOIN)

    rusr_messages[id] = {
        "msg": msg,
        "guild": ctx.guild,
        "channel": ctx.channel,
        "time": getts(),
        "uid": ctx.author.id,
        "state": "setup",
        "alive": [
            ctx.author.id
        ],
        "dead": []
    }

# Casino
@bot.command(name="lottery", help="Buy a lottery ticket.")
async def lottery(ctx):
    await ctx.send("Not implemented")

@bot.command(name="slots", help="Spin the slots for a chance to win the jackpot!")
async def slots(ctx):
    await ctx.send("Not implemented")

@bot.command(name="spin", help="Spin the wheel every 5 minutes for a reward.")
async def spin(ctx):
    ods = [
        { "symbol": "<:c500:710482148305403924>", "propbability": 1, "ods": 500, "name": "MYTHIC" },
        { "symbol": "<:c100:710482154500653056>", "propbability": 1, "ods": 100, "name": "IMORTAL" },
        { "symbol": "<:c50:710482156895469691>", "propbability": 2, "ods": 50, "name": "LEGENDARY" },
        { "symbol": "<:c25:710482155310022758>", "propbability": 4, "ods": 25, "name": "EPIC" },
        { "symbol": "<:c10:710482151484817439>", "propbability": 8, "ods": 10, "name": "RARE" },
        { "symbol": "<:c5:710482137895403520>", "propbability": 12, "ods": 5, "name": "UNCOMMON" },
        { "symbol": "<:c1:710482104705613845>", "propbability": 24, "ods": 1, "name": "COMMON" }
    ]

    usr = load_user(ctx.guild.id, ctx.author.id)

    if not "casino" in usr:
        usr["casino"] = {}
    if not "last_spin" in usr["casino"]:
        usr["casino"]["last_spin"] = 0

    if getts() - usr["casino"]["last_spin"] < 300:
        await ctx.send("You have to wait " + sec2human(300 - (getts() - usr["casino"]["last_spin"])) + " for your next chance of a reward.")
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

    embed = discord.Embed(
        title = ctx.author.display_name + " spins the wheel ...",
        description = "<a:spin:710491435006165032> | Spinning ...",
        colour = discord.Colour.green()
    )

    msg = await ctx.send(embed=embed)

    time.sleep(1)

    embed = discord.Embed(
        title = ctx.author.display_name + " Spun the wheel",
        description = out["symbol"] + " | Landed on **" + out["name"] + "**\nYou got a bonus of +" + str(out["ods"]) + " coins",
        colour = discord.Colour.green()
    )

    await msg.edit(embed=embed)

    usr["coins"] = usr["coins"] + out["ods"]
    usr["casino"]["last_spin"] = getts()
    save_user(usr)

@bot.command(name="scratch", help="Scratch a card for a chanceto win a reward.")
async def scratch(ctx):
    await ctx.send("Not implemented")

@bot.command(name="dice", help="Roll the dice, if you roll a 6 you'll get your bet x5!")
async def dice(ctx):
    await ctx.send("Not implemented")

@bot.command(name="snakeeyes", help="Two dice are rolled. Roll a 1 on either one to win. Get both on 1 to recieve a special bonus reward.")
async def snakeeyes(ctx):
    await ctx.send("Not implemented")

@bot.command(name="blackjack", help="Play a game of blackjack.")
async def snakeeyes(ctx):
    await ctx.send("Not implemented")

# Moderation

@bot.command(name="clear", help="Clears some messages from the history")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amt = 10):
    if not type(amt) is int:
        try:
            amt = int(amt, 10)
        except ValueError:
            await ctx.send("Invalid number of messages given")
            return

    if amt < 1:
        await ctx.send("Can not remove " + str(amt) + " messages")
        return
    elif amt > 100:
        amt = 100

    await ctx.channel.purge(limit=amt + 1)

    await print_audit(ctx.guild.id, "clear", ctx.author.id, "Cleared " + str(amt) + " messages from channel <#" + str(ctx.channel.id) + ">")

@bot.command(name="kick", help="Kicks a user from the server")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason = None):

    if reason is None:
        await print_audit(ctx.guild.id, "kick", ctx.author.id, "Kicked " + member.name + "#" + member.discriminator + " for no reason.")
    else:
        await print_audit(ctx.guild.id, "kick", ctx.author.id, "Kicked " + member.name + "#" + member.discriminator + " for **\"" + str(reason) + "\"**.")

    if reason is None:
        reason = "No reason given"

    embed = discord.Embed(
        title = ":information_source: " + ctx.guild.name + ": You have been kicked!",
        description = "Reason: " + reason,
        colour = discord.Colour.dark_orange()
    )

    await member.send(embed=embed)

    # We need to send the message first because discord does not let you send messages to users that have no servers in common
    await member.kick(reason=reason)

    # Append to user history
    usr = load_user(ctx.guild.id, member.id)
    histentry = {
        "type": "kick",
        "time": getts(),
        "by": ctx.author.id,
        "reason": reason
    }
    usr["history"].append(histentry)
    save_user(usr)

@bot.command(name="ban", help="Bans a user from the server")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason = None):
    if reason is None:
        await print_audit(ctx.guild.id, "ban", ctx.author.id, "Baned " + member.name + "#" + member.discriminator + " for no reason.")
    else:
        await print_audit(ctx.guild.id, "ban", ctx.author.id, "Baned " + member.name + "#" + member.discriminator + " for **\"" + str(reason) + "\"**.")

    if reason is None:
        reason = "No reason given"

    # Time ban
    time = -1
    times = "Permanent"

    if time > 0:
        times = sec2human(time)

    embed = discord.Embed(
        title = ":no_entry_sign: " + ctx.guild.name + ": The BAN-HAMMER has spoken!",
        description = "Reason: " + reason + "\nTime: " + times,
        colour = discord.Colour.red()
    )

    await member.send(embed=embed)

    # We need to send the message first because discord does not let you send messages to users that have no servers in common
    await member.ban(reason=reason)

    # Append to user history
    usr = load_user(ctx.guild.id, member.id)
    histentry  = {
        "type": "ban",
        "duration": time,
        "time": getts(),
        "by": ctx.author.id,
        "reason": reason
    }
    usr["history"].append(histentry)
    save_user(usr)

@bot.command(name="warn", help="Warns a user")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member : discord.Member, *, reason = None):

    # Append to user history
    usr = load_user(ctx.guild.id, member.id)
    histentry = {
        "type": "warning",
        "time": getts(),
        "by": ctx.author.id,
        "reason": reason
    }
    usr["history"].append(histentry)
    save_user(usr)

    if reason is None:
        await print_audit(ctx.guild.id, "warn", ctx.author.id, "Warned " + member.name + "#" + member.discriminator + " for no reason.")
    else:
        await print_audit(ctx.guild.id, "warn", ctx.author.id, "Warned " + member.name + "#" + member.discriminator + " for **\"" + str(reason) + "\"**.")

    if reason is None:
        reason = "No reason given"

    embed = discord.Embed(
        title = ":warning: " + ctx.guild.name + ": You have been warned!",
        description = "Reason: " + reason,
        colour = discord.Colour.red()
    )

    await member.send(embed=embed)

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

@bot.command(name="ticket", help="Manages tickets")
async def ticket(ctx, action = None, *, name = None):
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
@tasks.loop(seconds=VOICE_TIMEOUT)
async def update_voice():
    print("Processing Voice Channel Memberships")

    # For all voice channels on each guild
    for guild in bot.guilds:

        # Do not do anything for unavailable guilds
        if guild.unavailable == True:
            continue

        for vchannel in guild.voice_channels:
            vchmem = len(vchannel.members)

            # No need to look into a voice channel with one or no active members
            if vchmem < 2:
                continue

            # For each current member
            for member in vchannel.members:
                if member.voice.afk:
                    continue
                elif member.voice.deaf or member.voice.self_deaf:
                    continue
                elif member.voice.mute or member.voice.self_mute:
                    continue

                usr = load_user(guild.id, member.id)
                usr['voice']['time'] = usr['voice']['time'] + VOICE_TIMEOUT
                usr['coins'] = usr['coins'] + VOICE_BONUS_COINS

                # Give an xp bonus for more people in the voicechat
                usr['xp'] = usr['xp'] + VOICE_BONUS_XP + (vchmem - 2)

                save_user(usr)

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

@tasks.loop(seconds=RUSR_TIMEOUT)
async def update_rusr():
    if len(rusr_messages) == 0:
        return

    print("Processing RusR Messages")

    for id in rusr_messages:
        game = rusr_messages[id]
        guild = game["guild"]

        # Do not do anything for unavailable guilds
        if guild.unavailable == True:
            continue

        ts = game["time"]
        tsd = getts() - ts
        state = game["state"]
        msg = game["msg"]

        if state == "setup" and tsd > 20:
            if len(game["alive"]) < 2:
                rusr_messages.pop(id, None)

                await msg.clear_reactions()
                await msg.edit(content="Not enougth players joined the game.", delete_after=5)
                return

            game["state"] = "running"
            game["index"] = 0
            game["time"] = getts()

            print(game)

            current = game["alive"][game["index"]]
            print(current)
            embed = discord.Embed(
                title = "Russian Roulette",
                description = "<@" + str(current) + ">, it is now your turn. React with " + EMOJI_FIRE + " to pull the trigger..."
            )
            # Alive / Graveyard
            get_rusr_fields(game, embed)

            await msg.clear_reactions()
            await msg.edit(embed=embed)
            await msg.add_reaction(EMOJI_FIRE)

            rusr_messages[id] = game

        elif state == "running" and tsd > 20:
            old = game["alive"][game["index"]]
            # Kill current player because of inactivity
            game["alive"].remove(old)
            game["dead"].append(old)

            print(game)
            # Determine current player
            current = game["alive"][game["index"]]
            game["index"] = game["index"] % len(game["alive"])

            if len(game["alive"]) == 1:
                # One player left

                embed = discord.Embed(
                    title = "Russian Roulette",
                    description = "<@" + str(old) + "> died of old age.",
                    colour = discord.Colour.red()
                )
                # Alive / Graveyard
                get_rusr_fields(game, embed)

                await msg.clear_reactions()
                await msg.edit(embed=embed)

                game["state"] = "winner"

            else:
                # More than one player left
                embed = discord.Embed(
                    title = "Russian Roulette",
                    description = "<@" + str(old) + "> died of old age.\n<@" + str(current) + ">, it is now your turn. React with " + EMOJI_FIRE + " to pull the trigger...",
                    colour = discord.Colour.red()
                )
                # Alive / Graveyard
                get_rusr_fields(game, embed)

                await msg.clear_reactions()
                await msg.edit(embed=embed)
                await msg.add_reaction(EMOJI_FIRE)

            game["time"] = getts()
            rusr_messages[id] = game

        elif state == "winner" and tsd > 20:
            current = game["alive"][0]
            user = bot.get_user(current)
            embed = discord.Embed(
                title = "Russian Roulette",
                description = "<@" + str(current) + "> is the lone survivor. Congratulations!",
                colour = discord.Colour.green()
            )
            embed.set_thumbnail(url=user.avatar_url)

            # Alive / Graveyard
            get_rusr_fields(game, embed)

            await msg.edit(embed=embed)
            rusr_messages.pop(id)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        print("Loading cog: %s" % filename)
        bot.load_extension("cogs.%s" % filename[:-3])

update_voice.start()
update_nicknames.start()
update_help.start()
update_rusr.start()
print(f'Cassandra has connected to Discord!')

bot.run(TOKEN)
