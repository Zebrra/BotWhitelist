#! /usr/bin/python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json


from .Files import PrefixJson

class HelpCog(commands.Cog, name='Help'):

    """Pour utiliser la commande help : help [nom du cog] ou [commande]"""

    def __init__(self, bot):
        self.bot = bot
        self.__json_prefix = PrefixJson().get_prefix_path()

    @commands.command() #hidden = True
    async def help(self, ctx, *cog):

        """Liste des commandes du bot\n"""

        if not cog:
            embed = discord.Embed(
                color= 0x0D165A
            )
            cog_description = ''
            for i in self.bot.cogs:
                cog_description += ('**{}** - {}'.format(i, self.bot.cogs[i].__doc__) + '\n')
            embed.add_field(name='Liste des cogs', value=cog_description[0:len(cog_description) - 1], inline= False)
            await ctx.message.add_reaction(emoji='📧')
            await ctx.send(embed= embed)
        
        else:
            if len(cog) > 1:
                embed = discord.Embed(
                    title= "Erreur",
                    description= "Trop de cogs dans les paramètres",
                    color= 0x0D165A
                )
            else:
                found = False
                for i in self.bot.cogs:
                    for e in cog:
                        if i == e:
                            embed = discord.Embed(
                                color= 0x0D165A
                            )
                            scog_info = ''
                            for c in self.bot.get_cog(e).get_commands():
                                if not c.hidden:
                                    scog_info += f'**{c.name}** - {c.help}\n'
                            embed.add_field(name= f"{cog[0]} Module - {self.bot.cogs[cog[0]].__doc__}", value= scog_info)
                            found = True
            
                if not found:
                    for i in self.bot.cogs:
                        for c in self.bot.get_cog(i).get_commands():
                            if c.name == cog[0]:
                                embed = discord.Embed(color= 0x0D165A)
                                embed.add_field(name= f"{c.name} - {c.help}", value= f"Syntaxe correcte :\n``{c.qualified_name} {c.signature}``")
                                found = True

                if not found:
                    embed = discord.Embed(
                        title= "Error",
                        description= 'Comment veux tu utiliser "'+ cog[0]+'"?',
                        color= 0x0D165A)

                else:
                    await ctx.message.add_reaction(emoji="📧")
                await ctx.send(embed= embed)

    @commands.command()
    async def listing(self, ctx):

        """Liste l'ensemble des commandes du bot"""

        with open(self.__json_prefix, "r") as f:
                prefixes = json.load(f)

        pre = prefixes[str(ctx.guild.id)]


        embed = discord.Embed(
            colour = 0x0D165A,
            title = "Liste des commandes du bot"
        )
        scog_info = ''
        for i in self.bot.cogs:
            scog_info += ('\n\n**{}** - {}'.format(i, self.bot.cogs[i].__doc__) + '\n')
            for c in self.bot.get_cog(i).get_commands():
                scog_info += ('{} - {}'.format(c.name, c.help) + '\n')
        embed.add_field(name=f"Le préfixe est ``{pre}``", value=scog_info)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpCog(bot))
    print("The cog Help is loaded")