import discord

from datetime import datetime as dt
from discord.ext import commands
from discord.ext.commands import Cog as cog

from utils.all import *


# SOME INFO
# commands.check() decorator didn't work, adding manual check function for now

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _filter_message(self, message: discord.Message):
        guild_id = message.guild.id
        formatted_message = ''.join(message.content.lower().split())
        filtered_words = self.bot.fetch("SELECT word_filter FROM guild_info WHERE guild_id={}".format(guild_id))
        if message.author.permissions_in(message.channel).manage_messages:
            return  # Guild has no word filter

        try:
            filtered_words[0].split()
        except (AttributeError, TypeError):
            return

        for word in filtered_words[0].split('||'):
            if word and word in formatted_message:
                await message.delete()
                return await message.channel.send(f"{message.author.mention}, you said a blacklisted word :eyes:")

    @cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        if message.content.lower().startswith('s!help'):
            return

        await self._filter_message(message)

    #
    @cog.listener()
    async def on_message_edit(self, before, after):
        ctx = await self.bot.get_context(before)
        if not log_channel(self.bot, ctx.guild):
            return

        if before.content == after.content:  # on_message_edit also triggers when an embed is sent
            return  # We don't want to log this, else it will raise errors

        content_dict = {
            "Author": f"{before.author} | {before.author.id}",
            "Before": before.content,
            "After": after.content,
            "Message ID": before.id,
            "Channel": f"{before.channel.mention} | {before.channel}",
            "Jump": before.jump_url
        }

        await log_channel(self.bot, ctx.guild).send(
            embed=embed_from_dict(
                title='Message Edit',
                colour=colours.msg_edit,
                content=content_dict,
            )
        )

    @cog.listener()
    async def on_message_delete(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        if not log_channel(self.bot, ctx.guild):
            return

        content_dict = {
            "Author": f"{message.author}\n**ID:** {message.author.id}",
            "Channel": f"{message.channel.mention} | {message.channel}",
            "Content": message.content
        }

        await log_channel(self.bot, ctx.guild).send(
            embed=embed_from_dict(
                title="Message Delete",
                colour=colours.msg_delete,
                content=content_dict,
                footer=(f"ID: {message.id}", None)
            )
        )

    @cog.listener()
    async def on_bulk_message_delete(self, messages):
        guild = messages[0].guild
        if not log_channel(self.bot, guild):
            return

        fmt = ''
        for message in messages:
            created = message.created_at.strftime("%d %B %Y, %H:%M:%S")
            fmt += f"Sent by: {message.author}\nAt: {created}\n" \
                f"Author ID: {message.author.id}\nContent: {message.content}\n\n\n"
        url = await post_hastebin(fmt)

        emb = discord.Embed(
            title=f"{len(messages)} message(s) purged",
            description=f"Further information can be found here:\n{url}",
            colour=discord.Colour.light_grey(),
            timestamp=dt.utcnow()
        )
        await log_channel(self.bot, guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_guild_channel_update(self, before, after):
        guild = before.guild
        if not log_channel(self.bot, guild):
            return
        content_dict = {}

        if before.name != after.name:
            content_dict["Old Name"] = before.name
            content_dict["New Name"] = after.name

        if before.position != after.position:
            content_dict["Old Position"] = str(before.position)
            content_dict["New Position"] = str(after.position)

        if before.category != after.category:
            content_dict["Old Category"] = before.category.name
            content_dict["New Category"] = after.category.name

        if content_dict.keys():
            await log_channel(self.bot, guild).send(
                embed=embed_from_dict(
                    title='Category/Channel Update',
                    colour=colours.channel_update,
                    content=content_dict,
                    footer=(f"Channel ID: {before.id}", None)
                )
            )

    @cog.listener()
    async def on_member_update(self, before, after):
        guild = before.guild
        if not log_channel(self.bot, guild):
            return

        content_dict = {}

        if before.nick != after.nick:
            content_dict["Old nickname"] = before.nick
            content_dict["New nickname"] = after.nick

        if before.avatar != after.avatar:
            content_dict["Avatar Update"] = after.avatar_url

        if before.roles != after.roles:
            new_role = [role.name for role in after.roles if role not in before.roles]
            new_role2 = [role.name for role in before.roles if role not in after.roles]

            if new_role and not new_role2:
                content_dict["New role/s"] = '\n'.join(new_role)
            elif new_role2 and not new_role:
                content_dict["Removed role/s"] = '\n'.join(new_role2)
            else:
                content_dict["New role/s"] = '\n'.join(new_role)
                content_dict["Removed role/s"] = '\n'.join(new_role2)

        if str(before) != str(after):
            content_dict["Old username"] = str(before)
            content_dict["New username"] = str(after)

        if content_dict.keys():
            await log_channel(self.bot, guild).send(
                embed=embed_from_dict(
                    title="Member Update",
                    colour=colours.member_update,
                    content=content_dict,
                    footer=(f"ID: {before.id}", None)
                )
            )

    @cog.listener()
    async def on_guild_update(self, before, after):
        if not log_channel(self.bot, after):
            return

        content_dict = {}

        if before.name != after.name:
            content_dict["Old name"] = before.name
            content_dict["New name"] = after.name

        if before.region != after.region:
            content_dict["Old region"] = before.region
            content_dict["New region"] = after.region

        if before.mfa_level != after.mfa_level:
            content_dict["Old MFA level"] = before.mfa_level
            content_dict["New MFA level"] = after.mfa_level

        if before.verification_level != after.verification_level:
            content_dict["Old verification level"] = before.verification_level
            content_dict["New verification level"] = after.verification_level

        if before.explicit_content_filter != after.explicit_content_filter:
            content_dict["Old explicit content filter"] = before.explicit_content_filter
            content_dict["New explicit content filter"] = after.explicit_content_filter

        if before.default_notifications != after.default_notifications:
            content_dict["Old notification level"] = before.default_notifications
            content_dict["New notification level"] = after.default_notifications

        if before.categories != after.categories:
            content_dict[
                "Category changes"
            ] = f"__Before__: {', '.join(before.categories)}\n__After__: {', '.join(after.categories)}"

        if before.owner != after.owner:
            content_dict["Old owner"] = f"{before.owner.mention} | {before.owner}"
            content_dict["New owner"] = f"{after.owner.mention} | {after.owner}"

        if content_dict.keys():
            await log_channel(self.bot, after).send(
                embed=embed_from_dict(
                    title="Guild updates",
                    colour=colours.server_update,
                    content=content_dict,
                )
            )

    @cog.listener()
    async def on_member_ban(self, guild, member):
        if not log_channel(self.bot, guild):
            return

        # TODO: fix clashing events with moderation.py
        emb = discord.Embed(
            title="Member Ban",
            colour=colours.member_ban,
            description=str(member),
            timestamp=dt.utcnow(),
        )

        if isinstance(member, discord.Member):
            emb.set_footer(
                text=f"ID: {member.id}",
                icon_url=member.avatar_url
            )

        await log_channel(self.bot, guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_member_unban(self, guild, user):
        if not log_channel(self.bot, guild):
            return

        emb = discord.Embed(
            title="Member Unban",
            colour=colours.member_unban,
            description=f"{user} | {user.id}",
            timestamp=dt.utcnow()
        )
        await log_channel(self.bot, guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_guild_channel_pins_update(self, channel, _):
        if not log_channel(self.bot, channel.guild):
            return

        emb = discord.Embed(
            title="Message pin/unpin",
            description=f"Pin updated in {channel.mention} | {channel}",
            timestamp=dt.utcnow()
        )
        await log_channel(self.bot, channel.guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_guild_channel_create(self, channel):
        if not log_channel(self.bot, channel.guild):
            return

        emb = discord.Embed(
            title='Channel created',
            description=str(channel),
            timestamp=dt.utcnow()
        )
        await log_channel(self.bot, channel.guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not log_channel(self.bot, channel.guild):
            return

        emb = discord.Embed(
            title='Channel deleted',
            description=str(channel),
            timestamp=dt.utcnow(),
        )
        emb.set_footer(text=f"ID: {channel.id}")
        await log_channel(self.bot, channel.guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_member_join(self, member):
        if not log_channel(self.bot, member.guild):
            return

        now = dt.utcnow()
        join_format = now.strftime("%d %B %Y, %H:%M:%S")

        creation_date = member.created_at
        time_diff = (dt.utcnow() - creation_date)
        create_format = creation_date.strftime("%d %B %Y, %H:%M:%S")

        content_dict = {
            "Username": f"{member}",
            "Joined at": join_format,
            "Created at": f"{create_format} ({time_diff} days ago)"
        }

        emb = embed_from_dict(
            title="Member Join",
            colour=colours.member_join,
            content=content_dict,
            footer=(f"ID: {member.id}", None)
        )
        if member.avatar_url:
            emb.set_thumbnail(url=str(member.avatar_url))

        await log_channel(self.bot, member.guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_member_remove(self, member):
        if not log_channel(self.bot, member.guild):
            return

        now = dt.utcnow()
        join_format = now.strftime("%d %B %Y, %H:%M:%S")

        creation_date = member.created_at
        time_diff = (dt.utcnow() - creation_date)
        create_format = creation_date.strftime("%d %B %Y, %H:%M:%S")

        content_dict = {
            "Username": str(member),
            "Joined at": join_format,
            "Created at": f"{create_format} ({time_diff} days ago)"
        }

        emb = embed_from_dict(
            title="Member Leave",
            colour=colours.member_leave,
            content=content_dict,
            footer=(f"ID: {member.id}", None)
        )
        if member.avatar_url:
            emb.set_thumbnail(url=str(member.avatar_url))

        await log_channel(self.bot, member.guild).send(
            embed=emb
        )

    @cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not log_channel(self.bot, role.guild):
            return

        if role.permissions.administrator:
            perm_list = 'Administrator'
        else:
            perm_list = ''
            for perm, value in role.permissions:
                if value:  # Only append permission that the role has
                    perm_list += f"{perm}\n"

        content_dict = {
            "Role name": role.name,
            "Permissions": perm_list,
            "Created at": role.created_at.strftime("%d %B %Y, %H:%M:%S"),
            "Integrated?": role.managed,
            "Mentionable": role.mentionable
        }

        await log_channel(self.bot, role.guild).send(
            embed=embed_from_dict(
                title="Role created",
                colour=role.colour,
                content=content_dict,
                footer=(f"ID: {role.id}", None)
            )
        )

    @cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not log_channel(self.bot, role.guild):
            return

        emb = discord.Embed(
            title='Role deleted',
            description=f"**Role name:** {role.name}",
            colour=role.colour,
            timestamp=dt.utcnow(),
        )
        emb.set_footer(
            text=f"ID: {role.id}"
        )

        await log_channel(self.bot, role.guild).send(
            embed=emb
        )


def setup(bot):
    bot.add_cog(Logger(bot))
