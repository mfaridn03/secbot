import asyncio
import string

import discord

from discord.ext import commands


class Server(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot
        self.image_only_emote = '⭕'  # Circle
        self.q_only_emote = '🔺'  # Triangle
        self.reformat_input = set(letter for letter in (string.ascii_lowercase + '1234567890'))

    def cog_unload(self):
        self.bot.conn.close()

    def _past_setup_check(self, ctx, column):
        statement = f"SELECT {column} FROM guild_info WHERE guild_id={ctx.guild.id}"
        c = self.bot.execute(statement)
        if c.fetchone() is not None:
            return True
        return False

    def _set_guild_security(self, ctx, type_: int = None, disable=False):
        # security_type column
        if disable:
            self.bot.execute(
                "UPDATE guild_info SET security_type=NULL WHERE guild_id={}".format(ctx.guild.id)
            )
        else:
            check = self._past_setup_check(ctx, 'security_type')
            if check:
                self.bot.execute(
                    "UPDATE guild_info SET security_type=? WHERE guild_id=?",
                    (type_, ctx.guild.id)
                )
            else:
                self.bot.execute(
                    "INSERT INTO guild_info (guild_id, security_type) VALUES (?, ?)",
                    (ctx.guild.id, type_)
                )
        self.bot.commit()

    def _set_log_channel(self, ctx, channel: int = None):
        # log_channel column
        if not channel:
            self.bot.execute(
                "UPDATE guild_info SET log_channel=NULL WHERE guild_id={}"
                    .format(ctx.guild.id)
            )
            self.bot.execute(
                "UPDATE guild_info SET unverified_role=NULL WHERE guild_id={}"
                    .format(ctx.guild.id)
            )
        else:
            check = self._past_setup_check(ctx, 'log_channel')
            if check:
                self.bot.execute(
                    "UPDATE guild_info SET log_channel=? WHERE guild_id=?",
                    (channel, ctx.guild.id)
                )
            else:
                self.bot.execute(
                    "INSERT INTO guild_info (guild_id, log_channel) VALUES (?, ?)",
                    (ctx.guild.id, channel)
                )
        self.bot.commit()

    def _set_unverified_role(self, ctx, role_id: int):
        # unverified_role column
        check = self._past_setup_check(ctx, 'unverified_role')
        if check:
            self.bot.execute(
                "UPDATE guild_info SET unverified_role=? WHERE guild_id=?",
                (role_id, ctx.guild.id)
            )
        else:
            self.bot.execute(
                "INSERT INTO guild_info (guild_id, unverified_role) VALUES (?, ?)",
                (ctx.guild.id, role_id)
            )
        self.bot.commit()

    def _set_verified_role(self, ctx, role_id: int):
        # verified_role column
        check = self._past_setup_check(ctx, 'verified_role')
        if check:
            self.bot.execute(
                "UPDATE guild_info SET verified_role=? WHERE guild_id=?",
                (role_id, ctx.guild.id)
            )
        else:
            self.bot.execute(
                "INSERT INTO guild_info (guild_id, verified_role) VALUES (?, ?)",
                (ctx.guild.id, role_id)
            )
        self.bot.commit()

    @commands.has_permissions(administrator=True)
    @commands.group(name='setup')
    async def _setup(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                'No such setup. Do `s!help setup` for more info.'
            )

    @_setup.command(name='captcha')
    async def captcha(self, ctx, disable=None):
        """
        Setup server captcha. To disable captcha, type s!setup captcha disable
        Note: you need to create an "unverified" role first; a role where new users cannot send any messages
        """
        if disable:
            self._set_guild_security(ctx, disable=True)
            return await ctx.send("Captcha security disabled! Re-enable again by typing `s!setup captcha`")

        emb = discord.Embed(
            title='Captcha Setup',
            colour=discord.Colour.red(),
        )

        emb.description = "Do you have a member role (default role to give new members)? " \
                          "If you don't want a default role, type 'no role'"
        info_msg = await ctx.send(embed=emb)

        def msg_check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        msg = await self.bot.wait_for(
            'message',
            check=msg_check,
            timeout=10
        )

        await msg.delete()
        if msg.content.lower() in {'n', 'no'}:
            emb.description = "Please create the member role. If you don't want a member role, " \
                              "type 'no role' next time you run this setup"
            return await info_msg.edit(
                content=None,
                embed=emb,
                delete_after=30
            )

        elif msg.content.lower() in {'y', 'yes'}:
            emb.description = 'Enter the role name'
            await info_msg.edit(embed=emb)

            msg = await self.bot.wait_for(
                'message',
                check=msg_check,
                timeout=10
            )
            await msg.delete()
            try:
                role = await commands.RoleConverter().convert(ctx, msg.content)
            except commands.BadArgument:
                emb.description = "Role not found. Note: role search is not case sensitive, " \
                                  "but the exact name is needed"
                return await info_msg.edit(
                    content=None,
                    embed=emb,
                    delete_after=30
                )
            else:
                self._set_verified_role(ctx, role.id)

        emb.description = 'Do you have a role for unverified users? (y/n)'

        msg = await self.bot.wait_for(
            'message',
            check=msg_check,
            timeout=10
        )

        await msg.delete()
        if msg.content.lower() in {'n', 'no'}:
            emb.description = "You need to create a role, place it below the role 'xyzSecurity', " \
                              "turn every permission off and run the command again"
            return await info_msg.edit(
                content=None,
                embed=emb,
                delete_after=30
            )

        elif msg.content.lower() in {'y', 'yes'}:
            emb.description = 'Enter the role name'
            await info_msg.edit(embed=emb)

            msg = await self.bot.wait_for(
                'message',
                check=msg_check,
                timeout=10
            )
            await msg.delete()
            try:
                role = await commands.RoleConverter().convert(ctx, msg.content)
            except commands.BadArgument:
                emb.description = "Role not found. Note: role search is not case sensitive, " \
                                  "but the exact name is needed"
                return await info_msg.edit(
                    content=None,
                    embed=emb,
                    delete_after=30
                )
            else:
                self._set_unverified_role(ctx, role.id)

        emb.description = f"""
The bot currently supports 3 types of captcha verification:
- Image captcha
- Simple questions
- A combination of both

**__React to an emote to select the following security options. You have 15 seconds.__**
Image only: {self.image_only_emote}
Question only: {self.q_only_emote}
            """
        reaction_dict = {
            self.image_only_emote: [1, "Image only"],
            self.q_only_emote: [2, "Question only"],
        }
        await info_msg.edit(
            content=None,
            embed=emb,
        )
        for emote in [self.q_only_emote, self.image_only_emote]:
            await info_msg.add_reaction(emote)

        def check(r, u):
            return (
                    r.message.id == info_msg.id and
                    str(r) in {self.image_only_emote, self.q_only_emote} and
                    u == ctx.author
            )

        reaction, user = await self.bot.wait_for(
            'reaction_add',
            check=check,
            timeout=15
        )

        self._set_guild_security(ctx, reaction_dict[str(reaction.emoji)][0])
        emb.description = f"Done! Set security type to: `{reaction_dict[str(reaction.emoji)][1]}`"
        await info_msg.clear_reactions()
        return await info_msg.edit(
            content=None,
            embed=emb,
            delete_after=10
        )

    @captcha.error
    async def captcha_error(self, error, ctx):
        if isinstance(error, asyncio.TimeoutError):
            return await ctx.send("Timeout")

    @_setup.command(name='log')
    async def log(self, ctx, channel=None):
        """
        Change where logs are sent
        To disable logging, do s!setup log disable

        Logging logs the following events:
        - Message delete/edit
        - User profile update
        - Bans/unbans/kicks
        - Guild updates (e.g. new channel creation, guild settings change)
        - Role updates
        """

        if not channel:
            return await ctx.send(
                "For more information, type `s!help setup log`"
            )

        if str(channel).lower() == 'disable':
            self._set_log_channel(ctx)
            return await ctx.send("Done! Bot will no longer log. To revert, do `s!setup log #channel`")
        else:
            try:
                ch = await commands.TextChannelConverter().convert(ctx, channel)
            except commands.BadArgument:
                return await ctx.send("Channel not found")
            self._set_log_channel(ctx, ch.id)
            return await ctx.send(f"Done! Chatlogger will be logged in {ch.mention}")

    @commands.has_permissions(administrator=True)
    @commands.group(name='filter')
    async def _filter(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send("Unknown command. Type `s!help filter` for information")

    @_filter.command(name='add')
    async def filter_add(self, ctx, *words):
        """
        Add words to chat filter, separated by spaces. No symbols allowed, numbers are allowed
        e.g. s!filter add bad word boo 69 TR4SH
        """
        # yes very ugly iteration
        lowercase_converted = []
        for word in words:
            for letter in word:
                if letter.lower() not in self.reformat_input:
                    return await ctx.send(
                        "One or more of the words contain an unknown symbol. Only letters and numbers are allowed"
                    )
            lowercase_converted.append(word.lower())
        formatted_words = '||' + '||'.join(lowercase_converted)

        check = self._past_setup_check(ctx, 'word_filter')
        if check:
            current_list = self.bot.fetch(
                "SELECT word_filter FROM guild_info WHERE guild_id={}"
                    .format(ctx.guild.id)
            )[0]

            formatted_words = current_list + formatted_words
            self.bot.execute(
                "UPDATE guild_info SET word_filter='{}' WHERE guild_id={}".format(formatted_words, ctx.guild.id)
            )
            self.bot.commit()
            e = self.bot.fetch("SELECT word_filter FROM guild_info WHERE guild_id={}".format(ctx.guild.id))[0]
        else:
            self.bot.execute(
                "INSERT INTO guild_info (guild_id, word_filter) VALUES (?, ?)",
                (ctx.guild.id, formatted_words)
            )
            self.bot.commit()
            e = self.bot.fetch("SELECT word_filter FROM guild_info WHERE guild_id={}".format(ctx.guild.id))[0]


def setup(bot):
    bot.add_cog(Server(bot))
