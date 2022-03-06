#! /usr/bin/python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands


class ErrorCog(commands.Cog, name='Error'):

    """Error handler (0 commande ne pas l'invoquer)"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            if hasattr(ctx.command, 'on_error'):
                return
            else:
                embed = discord.Embed(
                    title=f"Erreur avec {ctx.command}",
                    description= f"{ctx.command.qualified_name} {ctx.command.signature}\n{error}",
                    color= 0x437808
                )
                await ctx.send(embed= embed)

        except:
            embed = discord.Embed(
                title=f"Erreur avec {ctx.command}",
                description= f"{error}",
                color= 0x437808
            )
            await ctx.send(embed= embed)


def setup(bot):
    bot.add_cog(ErrorCog(bot))
    print("The cog Error is loaded")