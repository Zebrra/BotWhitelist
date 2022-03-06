#! /usr/bin/python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import traceback
import sys
import aiosqlite
import json

import cogs.Files as Files


def get_prefix(bot, message):
    with open(prefix_json, 'r') as f:
        prefixes = json.load(f)

    try:
        pre = prefixes[str(message.guild.id)]
    except:
        prefixes[str(message.guild.id)] = '!'
        with open(prefix_json, 'w') as f:
            json.dump(prefixes, f)
        pre = prefixes[str(message.guild.id)]
    return pre

bot = commands.Bot(command_prefix= get_prefix, intents = discord.Intents.all())
bot.remove_command('help')

async def find_prefix():
    guild = bot.get_guild(guild_id)

    with open(prefix_json, 'r') as f:
        prefixes = json.load(f)
    try:
        pre = prefixes[str(guild.id)]
    except:
        prefixes[str(guild.id)] = '!'
        with open(prefix_json, 'w') as f:
            json.dump(prefixes, f)
        pre = prefixes[str(guild.id)]

    print(f"Logged in as {bot.user}")
    return await bot.change_presence(activity= discord.Game(name= f"{pre}help"))

@bot.event
async def on_ready():
    main = await aiosqlite.connect(database)
    cursor = await main.cursor()

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS whitelist_inload(
            guild_id INTEGER,
            user_id INTEGER
        )
    ''')
    await main.commit()

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS whitelist_request(
            guild_id INTEGER,
            channel_name TEXT,
            channel_id INTEGER,
            user_id INTEGER
        )
    ''')
    await main.commit()

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS whitelist_setup(
            guild_id INTEGER,
            message_id INTEGER
        )
    ''')
    await main.commit()

    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS whitelist_text_answer(
            guild_id INTEGER,
            user_id INTEGER,
            user_name TEXT,
            age TEXT,
            name_rp TEXT,
            roleplay TEXT,
            pub TEXT,
            background TEXT
        )
    ''')
    await main.commit()

    await cursor.close()
    await main.close()

    await find_prefix()

@bot.event
async def on_guild_join(guild):
    with open(prefix_json, 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '!'

    with open(prefix_json, 'w') as f:
        json.dump(prefixes,f)


initial_extensions = [
    'cogs.cog_aahelp',
    'cogs.cog_error',
    'cogs.cog_prefix',
    'cogs.cog_setup_whitelist',
    'cogs.cog_event_whitelist'
]

if __name__ == '__main__':
    guild_id = Files.GuildId().get_guild_id_path()
    database = Files.Database().get_database_path()
    prefix_json = Files.PrefixJson().get_prefix_path()
    
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}", file=sys.stderr)
            traceback.print_exc()

bot.run(Files.Token().get_token_path())