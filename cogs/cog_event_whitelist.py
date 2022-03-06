#! /usr/bin/python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import sqlite3
import json
import datetime
import random

from .Files import GuildId, Database, WriteQuestionsJson, ReactQuestionsJson, NumberQuestion
from .Question import Question


class WhitelistCog(commands.Cog, name= "Cog Whitelist"):

    """Whitelist automatique"""

    def __init__(self, bot):
        self.bot = bot
        self.__guild_id = GuildId().get_guild_id_path()
        self.__main = Database().get_database_path()
        self.__json_write_questions = WriteQuestionsJson().get_write_questions_path()
        self.__json_react_questions = ReactQuestionsJson().get_react_questions_path()
        self.__number_question = NumberQuestion().number_question()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        guild_id = self.__guild_id
        guild = self.bot.get_guild(guild_id)

        user_id = reaction.user_id
        user = self.bot.get_user(user_id)

        channel_id = reaction.channel_id
        channel = self.bot.get_channel(channel_id)

        messageid = reaction.message_id
        emoji = reaction.emoji.name

        if user.bot == True:
            return

        if emoji != "🆕" and emoji != "✅" and emoji != "❌":
            return
        main = sqlite3.connect(self.__main)
        cursor = main.cursor()

        message_Id = cursor.execute(f"SELECT message_id FROM whitelist_setup WHERE guild_id = '{guild_id}'")
        result_message_id = message_Id.fetchone()

        if messageid == result_message_id[0] and emoji == "🆕" and user.bot == False:
            
            member = discord.utils.find(lambda m : m.id == reaction.user_id, guild.members)
            refused_role = discord.utils.get(guild.categories, name="❌")
            whitelist_role = discord.utils.get(guild.roles, name="✅Validé")

            if refused_role in member.roles:
                embed = discord.Embed(
                    color = 0xF42828,
                    title = f"{user.name} tu as échoué 3 fois, tu ne peux plus passer de questionnaire.",
                    description = "Demande au staff pour peut être retenter ta chance.."
                )
                return await user.send(embed=embed)

            if whitelist_role in member.roles:
                embed = discord.Embed(
                    color = 0xF42828,
                    title= f"{user.name} tu as déjà été validé.",
                    description= 'Pourquoi tiens tu tant à retenter ta chance ? Ton QCM a déjà été approuvé, tu ne peux pas le repasser.'
                )
                return await user.send(embed=embed)


            message = await channel.fetch_message(messageid)
            await message.remove_reaction("🆕", user)

            db_count = cursor.execute(f"SELECT COUNT(user_id) FROM whitelist_request WHERE guild_id = '{guild_id}' and user_id = '{user_id}'")
            result_db_count = db_count.fetchone()

            if result_db_count[0] == 1:

                embed = discord.Embed(
                    color = 0xF42828,
                    title = f"{user.name} tu as déjà un ticket-WL en attente.",
                    description = "Finis ton questionnaire avant de retenter ta chance.."
                )
                return await user.send(embed=embed)

            member = discord.utils.find(lambda m : m.id == reaction.user_id, guild.members)
            admin_role = discord.utils.get(guild.roles, name="Admin")
            mod_role = discord.utils.get(guild.roles, name="Modérateur")
            staff_role = discord.utils.get(guild.roles, name="Staff")
            category = discord.utils.get(guild.categories, name="WHITELIST")

            if admin_role is None:
                await guild.create_role(name="Admin")

            if mod_role is None:
                await guild.create_role(name="Modérateur")

            if staff_role is None:
                await guild.create_role(name="Staff")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            whitelist_channel_name = await category.create_text_channel(f"whitelist-{member.name.lower()}", overwrites=overwrites)
            whitelist_channel_id = whitelist_channel_name.id

            sql = ('INSERT INTO whitelist_request(guild_id, channel_name, channel_id, user_id) VALUES(?,?,?,?)')
            val = (guild_id, str(whitelist_channel_name), whitelist_channel_id, user_id)
            cursor.execute(sql, val)
            main.commit()

            embed = discord.Embed(
                color = 0xFF3C33, 
                description = f"Bienvenue **{member.name}** nous allons commencer la whitelist pour le serveur {guild}.\nJe vais te poser quelques questions et tu devras y répondre grâce aux réactions et choisir pour toi la bonne réponse en fonction des propositions que je te fais,\nil n'y aura qu'une bonne réponse sur quatre.."
            )
            embed.add_field(name="Est-ce que tu est prêt ?", value="Oui : ✅ | Non : ❌",inline=False)
            embed.set_footer(text="*Bonne chance !*")

            whitelist_channel_message = await whitelist_channel_name.send(embed=embed)
            await whitelist_channel_message.add_reaction("✅")
            await whitelist_channel_message.add_reaction("❌")

            cursor.close()
            main.close()
            return

        db_whitelist = cursor.execute(f"SELECT channel_id FROM whitelist_request WHERE guild_id = '{guild_id}'")
        result_db_whitelist = db_whitelist.fetchall()

        db_whitelist_channel_id = []
        for db_whitelist_id in result_db_whitelist:
            db_whitelist_channel_id.append(db_whitelist_id[0])

        user_whitelist = cursor.execute(f"SELECT user_id FROM whitelist_request WHERE guild_id = '{guild_id}' and channel_id = '{channel_id}'")
        result_user_whitelist = cursor.fetchone()

        if channel_id in db_whitelist_channel_id and emoji == "❌" and user.bot == False and user_id == result_user_whitelist[0]:

            message = await channel.fetch_message(messageid)
            await message.remove_reaction("❌", user)

            member = discord.utils.find(lambda m : m.id == reaction.user_id, guild.members)
            admin_role = discord.utils.get(guild.roles, name="Admin")
            mod_role = discord.utils.get(guild.roles, name="Modérateur")
            staff_role = discord.utils.get(guild.roles, name="Staff")

            db_channel_name = cursor.execute(f"SELECT channel_name FROM whitelist_request WHERE channel_id = '{channel_id}'")
            result_db_channel_name = db_channel_name.fetchone()

            embed = discord.Embed(
                color = 0xF42828,
                description= "**Le salon de whitelist se fermera dans 5 secondes**"
            )
            await channel.send(embed=embed)
            await asyncio.sleep(5)
            await channel.delete()

            cursor.execute(f"DELETE FROM whitelist_request WHERE channel_id = '{channel_id}'")
            main.commit()
            cursor.close()
            main.close()
            return


####################################################################################################################
##################################           CONDITION DU QUESTIONNAIRE           ##################################          
####################################################################################################################

        if channel_id in db_whitelist_channel_id and emoji == "✅" and user.bot == False and user_id == result_user_whitelist[0]:
            message = await channel.fetch_message(messageid)
            await message.remove_reaction("✅", user)

            citoyens_role = discord.utils.get(guild.roles, name="🌆Citoyens")
            whitelist_role = discord.utils.get(guild.roles, name="✅Validé")
            first_try_role = discord.utils.get(guild.roles, name="🔴")
            second_try_role = discord.utils.get(guild.roles, name="🔴🔴")
            refused_role = discord.utils.get(guild.roles, name="❌")

            if citoyens_role is None:
                await guild.create_role(name="🌆Citoyens")
            if whitelist_role is None:
                await guild.create_role(name="✅Validé")
            if first_try_role is None:
                await guild.create_role(name="🔴")
            if second_try_role is None:
                await guild.create_role(name="🔴🔴")
            if refused_role is None:
                await guild.create_role(name="❌")

            load_count = cursor.execute(f"SELECT COUNT(user_id) FROM whitelist_inload WHERE guild_id = '{guild_id}' and user_id = '{user_id}'")
            result_load_count = load_count.fetchone()

            if result_load_count[0] == 1:    
                embed = discord.Embed(
                    color = 0xF42828,
                    title = f"{user.name} tu as déjà lancé le questionnaire.",
                    description = "Finis ton questionnaire avant de retenter ta chance.."
                )
                return await channel.send(embed=embed)
            else:
                sql = ('INSERT INTO whitelist_inload(guild_id, user_id) VALUES(?,?)')
                val = (guild.id, user_id)
                cursor.execute(sql, val)
                main.commit()


            member = discord.utils.find(lambda m : m.id == reaction.user_id, guild.members)
            admin_role = discord.utils.get(guild.roles, name="Admin")
            mod_role = discord.utils.get(guild.roles, name="Modérateur")
            staff_role = discord.utils.get(guild.roles, name="Staff")
            category = discord.utils.get(guild.categories, name="WHITELIST")

            def check_message(message):
                return message.channel == channel and message.author == member
            
            embed_begin = discord.Embed(
                color = 0xFF3C33,
                description = "Avant de commencer le questionnaire, j'aimerais te poser 5 petites questions,\npour y répondre, tu as juste à écrire ta réponse dans le chat."
            )
            embed_begin.add_field(name="Temps de réponse :", value="```Pour la question n°1 : Tu as 2 minutes pour répondre.\nPour la question n°2 : Tu as 2 minutes pour répondre.\nPour la question n°3/4/5 : Tu as 6 minutes pour répondre.```", inline=False)
            embed_begin.set_author(name=guild.name, icon_url=guild.icon_url)
            embed_begin.timestamp = datetime.datetime.utcnow()
            await channel.send(embed=embed_begin)
            await asyncio.sleep(2)

            write_questions = []

            for element in json.load(open(self.__json_write_questions, encoding='utf-8')):
                questions = element.pop("write_prompt")
                write_questions.append(questions)

            c = 1
            n = 1
            t1 = 120
            t2 = 360
            write_answer = []
            for question in write_questions:
                write_embed = discord.Embed(
                    color = 0xF3A773,
                )
                write_embed.add_field(name=f"*Question n°{c}*", value=f"**{question}**", inline=False)
                await channel.send(embed=write_embed)
                c+=1
                if n<=2:
                    time = t1
                else:
                    time=t2
            
                write_question_answer = ""
                while write_question_answer == "":
                    try:
                        write_question_answer = await self.bot.wait_for("message", timeout=time, check=check_message)
                    except asyncio.TimeoutError:
                        write_question_answer = ""
                    else:
                        write_question_answer = write_question_answer.content
                    
                    if write_question_answer != "":
                        n+=1
                        write_answer.append(write_question_answer)
            
            key = 1
            answer_dict = {}
            for i in write_answer:
                answer_dict[key] = i
                key+=1

            whitelist_text_answer = cursor.execute(f"SELECT age, name_rp, roleplay, pub, background, user_name, user_id, guild_id FROM whitelist_text_answer WHERE guild_id = '{guild.id}' and user_id = '{member.id}'")
            result_whitelist_text_answer = whitelist_text_answer.fetchone()

            if result_whitelist_text_answer is None:
                sql = ('INSERT INTO whitelist_text_answer(age, name_rp, roleplay, pub, background, user_name, user_id, guild_id) VALUES(?,?,?,?,?,?,?,?)')
                val = (answer_dict[1], answer_dict[2], answer_dict[3], answer_dict[4], answer_dict[5], member.name, member.id, guild_id)
                cursor.execute(sql, val)
                main.commit()

            emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
            emoji_list2 = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
            def check_reaction(reaction, user):
                return user == member and user != self.bot.user and reaction.message == message_question and str(reaction.emoji) in emoji_list

            all_questions = []
            all_random_questions = []
            score = 0
            miss = 0
            loop = 1
            asked  = []
            answered = []
            missed_format = []
            all_format = []

            # ici je travaille sur mes objets
            for element in json.load(open(self.__json_react_questions, encoding='utf-8')):
                questions = element.pop("question_prompt")
                answers_prompt = element.pop("question_answers_prompt")
                answers = element.pop("question_answer")
                one_question = [Question(questions, answers_prompt, answers)]
                all_questions.append(one_question)

            for i in random.sample(all_questions, k=len(all_questions)):
                all_random_questions.append(random.choice(i))
                if len(all_random_questions) == self.__number_question:
                    break

            del all_questions

            for question in random.sample(all_random_questions, k=len(all_random_questions)):
                answer_prompt = "\n".join(f"{i}" for i in question.answer_prompt)
                react_embed = discord.Embed(
                    color = 0xF3A773
                )
                react_embed.add_field(name=f"*Question n°{loop}*", value=f"**{question.prompt}**\n{answer_prompt}")
                message_question = await channel.send(embed= react_embed)
                loop += 1
                for emoji in emoji_list:
                    await message_question.add_reaction(emoji)
                
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=20, check=check_reaction)
                except asyncio.TimeoutError:
                    missed_format.append("Non répondu, délai dépassé. (compte faux)")
                    miss+=1
                else:

                    index = emoji_list.index(reaction.emoji) + 1
                    index_e = emoji_list.index(reaction.emoji)

                    asked.append(question.prompt)
                    if index == question.answer:
                        score += 1
                        answered.append(question.answer_prompt[index_e])
                        all_format.append(f"✅ • {question.answer_prompt[index_e]}")

                    else:
                        miss += 1
                        for i in range(len(all_random_questions)):
                            if i+1 == question.answer:
                                good_answer_prompt = question.answer_prompt[i]
                                break

                        for e in range(len(all_random_questions)):
                            if emoji_list2[e] == emoji_list[index_e]:
                                answered.append(question.answer_prompt[e])
                                all_format.append(f"❌ • {question.answer_prompt[e]} | ✅ • {good_answer_prompt}")
                                missed_format.append(f"❌ • {question.answer_prompt[e]} | ✅ • {question.answer}")
                                break
        
            if first_try_role not in member.roles:
                role = first_try_role
            elif first_try_role in member.roles:
                await member.remove_roles(first_try_role)
                role = second_try_role
            elif second_try_role in member.roles:
                await member.remove_roles(second_try_role)
                role = refused_role


            await channel.send(f"Tu as {score} / {len(all_random_questions)}\nTu as loupé {miss} questions")
            if miss > 3:
                await channel.send(f"Tu as échoué au QCM whitelist.. Tu obtiens le rôle {role.mention}")
                await member.add_roles(role)
            else:
                await channel.send(f"Tu as réussi au QCM whitelist.. Tu es maintenant un {citoyens_role.mention}")
                await member.add_roles(citoyens_role)
                await member.add_roles(whitelist_role)

            result_category = discord.utils.get(guild.categories, name="RESULT-WHITELIST")
            
            if result_category is None:
                new_category = await guild.create_category(name="RESULT-WHITELIST")
                result_category = guild.get_channel(new_category.id)


            result_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                mod_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            result_whitelist_channel_name = await result_category.create_text_channel(f"result-wl-{member.name.lower()}", overwrites=result_overwrites)
            result_channel = self.bot.get_channel(result_whitelist_channel_name.id)

            result_for_whitelist = cursor.execute(f"SELECT age, name_rp, roleplay, pub, background, user_name, user_id, guild_id FROM whitelist_text_answer WHERE guild_id = '{guild_id}' and user_id = '{member.id}'")
            result_for_whitelist_answer = result_for_whitelist.fetchone()

            writed_embed = discord.Embed(
                color = 0xF3A773
            )
            writed_embed.set_author(name=member.name, icon_url=member.avatar_url)
            writed_embed.add_field(name="Son âge :", value = result_for_whitelist_answer[0], inline=False)
            writed_embed.add_field(name="Son personnage :", value = result_for_whitelist_answer[1], inline=False)
            writed_embed.add_field(name="Son roleplay :", value = result_for_whitelist_answer[2], inline=False)
            writed_embed.add_field(name="Comment il nous a connu :", value = result_for_whitelist_answer[3], inline=False)
            writed_embed.add_field(name="Son background :", value = result_for_whitelist_answer[4], inline=False)
            await result_channel.send(embed=writed_embed)


            format_answer1 = ''
            format_answer2 = ''
            format_answer3 = ''
            compt = 0
            if len(asked) == 15:
                for u in asked[0:5]:
                    compt+=1
                    format_answer1 += ('\n{}) {}\n{}'.format(compt, u, all_format[asked.index(u)]) + '\n')
                for e in asked[5:10]:
                    compt+=1
                    format_answer2 += ('\n{}) {}\n{}'.format(compt, u, all_format[asked.index(u)]) + '\n')
                for u in asked[10:15]:
                    compt+=1
                    format_answer3 += ('\n{}) {}\n{}'.format(compt, u, all_format[asked.index(u)]) + '\n')
            
            elif len(asked) == 10:
                for u in asked[0:5]:
                    compt+=1
                    format_answer1 += ('\n{}) {}\n{}'.format(compt, u, all_format[asked.index(u)]) + '\n')
                for e in asked[5:10]:
                    compt+=1
                    format_answer2 += ('\n{}) {}\n{}'.format(compt, u, all_format[asked.index(u)]) + '\n')

            elif len(asked) == 5:
                for u in asked[0:5]:
                    compt+=1
                    format_answer1 += ('\n{}) {}\n{}'.format(compt, u, all_format[asked.index(u)]) + '\n')

            react_answer_embed1 = discord.Embed(
                color=0xF3A773
            )
            react_answer_embed2 = discord.Embed(
                color=0xF3A773
            )
            react_answer_embed3 = discord.Embed(
                color=0xF3A773
            )
            react_answer_embed1.set_author(name=member.name, icon_url=member.avatar_url)
            react_answer_embed1.description = format_answer1
            await result_channel.send(embed=react_answer_embed1)

            react_answer_embed2.set_author(name=member.name, icon_url=member.avatar_url)
            react_answer_embed2.description = format_answer2
            await result_channel.send(embed=react_answer_embed2)

            react_answer_embed3.set_author(name=member.name, icon_url=member.avatar_url)
            react_answer_embed3.description = format_answer3
            await result_channel.send(embed=react_answer_embed3)

            close_embed = discord.Embed(
            colour = 0xff3c33,
            description = "Le channel se fermera dans 10 secondes .."
            )
            await channel.send(embed=close_embed)
            await asyncio.sleep(10)


            cursor.execute(f"DELETE FROM whitelist_inload WHERE user_id = '{user_id}'")
            main.commit()
            cursor.execute(f"DELETE FROM whitelist_request WHERE user_id = '{user_id}'")
            main.commit()
            cursor.execute(f"DELETE FROM whitelist_text_answer WHERE user_id = '{user_id}'")
            main.commit()
            await channel.delete()
            cursor.close()
            main.close()

            return


def setup(bot):
    bot.add_cog(WhitelistCog(bot))
    print("The cog Whitelist is loaded")