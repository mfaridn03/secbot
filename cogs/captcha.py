import asyncio
import os

import discord
from discord.ext import commands
from discord.ext.commands import Cog

from generators.generate_captcha import create_image
from generators.generate_question import create_question

cog = Cog  # Because it looks nice ;)


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending = {}

    def _captcha_setup_check(self, guild):
        guild_id = guild.id
        res = self.bot.fetch(
            "SELECT security_type FROM guild_info WHERE guild_id={}".format(guild_id)
        )
        if not res:
            return False
        return True

    @staticmethod
    async def incorrect_or(member: discord.Member):
        await member.send("Incorrect. Please rejoin and re-do the captcha")
        await member.kick(reason='Failed captcha')

    async def send_image_verification(self, member: discord.Member):
        image, text = create_image(member.id)

        emb = discord.Embed(title='Captcha Verification')
        emb.colour = 0xff0000  # Red
        emb.description = "Enter the letters in order of appearance, from left to right. You have 60 seconds."

        await member.send(
            embed=emb,
            file=discord.File(image)
        )
        os.remove(f"{member.id}.png")

        def check(msg):
            return msg.author.id == member.id and isinstance(msg.channel, discord.DMChannel)

        try:
            prompt = await self.bot.wait_for(
                'message',
                check=check,
                timeout=60
            )
        except asyncio.TimeoutError:
            await self.incorrect_or(member)
        else:
            if prompt.content.lower() == text:
                await member.send("Success!")
                return True
            else:
                await self.incorrect_or(member)
        return False  # Wrong input or took too long

    async def send_question_verification(self, member: discord.Member):
        answer = await create_question(member)

        def check(msg):
            return msg.author.id == member.id and isinstance(msg.channel, discord.DMChannel)

        try:
            m = await self.bot.wait_for(
                'message',
                check=check,
                timeout=60
            )
        except asyncio.TimeoutError:
            await self.incorrect_or(member)
        else:
            if m.content.lower() == answer:
                await member.send("Success!")
                return True
            else:
                await self.incorrect_or(member)
        return False

    async def initiate_captcha(self, guild, member_id, type_, unverified_role: discord.Role):
        target = guild.get_member(member_id)

        if member_id in self.pending.keys():
            await target.send("You failed a captcha. Come back in 1 minute")
            await target.kick()
            await asyncio.sleep(60)
            try:
                del self.pending[member_id]
            except KeyError:
                pass
            return

        self.pending[member_id] = True

        if int(type_) == 1:  # Image only
            res = await self.send_image_verification(target)
        else:
            res = await self.send_question_verification(target)

        if res:
            await target.remove_roles(unverified_role)
            del self.pending[member_id]

    @cog.listener()
    async def on_member_join(self, member: discord.Member):
        print('{} joined {}'.format(str(member), member.guild))
        if not self._captcha_setup_check(member.guild):
            return

        unv_role_id = self.bot.fetch(
            "SELECT unverified_role FROM guild_info WHERE guild_id={}"
                .format(member.guild.id)
        )[0]

        security_type = self.bot.fetch(
            "SELECT security_type FROM guild_info WHERE guild_id={}"
                .format(member.guild.id)
        )[0]

        unv_role = member.guild.get_role(int(unv_role_id))  # Just in case sqlite3 returns string :(
        await member.add_roles(unv_role)
        await self.initiate_captcha(member.guild, member.id, security_type, unv_role)


def setup(bot):
    bot.add_cog(Captcha(bot))
