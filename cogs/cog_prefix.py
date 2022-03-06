#! /usr/bin/python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import datetime


from .Files import PrefixJson

class PrefixCog(commands.Cog, name='Prefixe'):

    """Commandes relatives au préfixe du bot."""

    def __init__(self, bot):
        self.bot = bot
        self.__json_prefix = PrefixJson().get_prefix_path()

    @commands.command()
    async def show_prefix(self, ctx):
        with open(self.__json_prefix, "r") as f:
            prefixes = json.load(f)

        pre = prefixes[str(ctx.guild.id)]
        
        contexte = ctx.channel

        embed = discord.Embed(
            colour = 0xE67D2F,
            title = f"Mon prefixe pour ce serveur est '{pre}'"
        )
        embed.add_field(name="Ma commande pour changer mon prefixe est :", value=f"{pre}change_prefix <prefixe>", inline=True)
        embed.set_thumbnail(url= contexte.guild.icon_url)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.channel.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def change_prefix(self, ctx, prefix: str):
        with open(self.__json_prefix, "r") as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open(self.__json_prefix, "w") as f:
            json.dump(prefixes,f)

        embed = discord.Embed(
            colour = 0xE67D2F
        )
        embed.add_field(name="Préfixe", value=f"Mon prefixe pour ce serveur à été modifié par ``{prefix}``", inline=True)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)
        return await self.bot.change_presence(activity= discord.Game(name= f"{prefix}help"))


def setup(bot):
    bot.add_cog(PrefixCog(bot))
    print("The cog Prefix is loaded")