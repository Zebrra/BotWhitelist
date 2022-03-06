#! /usr/bin/python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import sqlite3
import datetime

from .Files import Database

class SetupWhitelistCog(commands.Cog, name="Cog setup WL"):

    """Permet de setup le système de WL"""

    def __init__(self, bot):
        self.bot = bot
        self.__main = Database().get_database_path()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_whitelist(self, ctx):

        guild_id = ctx.guild.id
        guild = self.bot.get_guild(guild_id)

        main = sqlite3.connect(self.__main)
        cursor = main.cursor()
        cursor.execute(f"SELECT guild_id, message_id FROM whitelist_setup WHERE guild_id = '{guild_id}'")
        result = cursor.fetchone()
        if result is None:
            category = discord.utils.get(guild.categories, name="WHITELIST")
            NWL_role = discord.utils.get(guild.roles, name="Non-Whitelist")

            if category is None:
                new_category = await guild.create_category(name="WHITELIST")
                category = discord.utils.get(guild.categories, id=new_category.id)

            if NWL_role is None:
                new_role = await guild.create_role(name="Non-Whitelist")
                NWL_role = discord.utils.get(guild.roles, id=new_role.id)

            overwrites =  {
                guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                NWL_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            channel = discord.utils.get(guild.text_channels, name="ticket-whitelist")

            if channel is None:
                channel = await category.create_text_channel("ticket-whitelist", overwrites=overwrites)

                embed = discord.Embed(
                    color = 0xFF3C33,
                    description = f"Bonjour et bienvenue sur le serveur {guild}.\n Voici le système de Whitelist automatique mis en place pour aider notre staff et rendre votre adhésion au sein de notre serveur plus rapide 😉"
                )
                embed.add_field(name="Envie de faire partie de la Whitelist ?", value="Pas de soucis clique sur la réaction suivante > 🆕\nEt répond à notre questionnaire, notre bot s'occupe du reste", inline=False)
                embed.set_footer(text="*Tout abus sera sanctionné*", icon_url=guild.icon_url)

                msg = await channel.send(embed=embed)
                await msg.add_reaction("🆕")

                sql = ('INSERT INTO whitelist_setup(guild_id, message_id) VALUES(?,?)')
                val = (guild_id, msg.id)

                cursor.execute(sql, val)
                main.commit()
                
                cursor.close()
                main.close()
                return
                
        else:
            embed = discord.Embed(
                color = 0xF42828,
                description = "Un problème est survenu, le salon existe déjà, impossible d'en crée un deuxième.."
            )
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()

            await ctx.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(SetupWhitelistCog(bot))
    print("The cog SetupWhitelist is loaded")