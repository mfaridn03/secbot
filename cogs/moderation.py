import discord

from datetime import datetime as dt
from discord.ext import commands
from utils.all import log_channel


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user, *, reason=None):
        """
        Kicks a member. Requires the kick_member permission
        """
        if not reason:
            reason = "Unspecified"
        try:
            target = await commands.MemberConverter().convert(ctx, user)
            await target.send(f"You were kicked out of {ctx.guild} for reason: {reason}")
            await target.kick(reason=reason)
        except (commands.BadArgument, discord.Forbidden) as error:
            if isinstance(error, commands.BadArgument):
                return await ctx.send("Member not found. Try mentioning them (or they left)")
        else:
            emb = discord.Embed(
                title='Member Kicked',
                description=f"Name: {target}\nExecuted by {ctx.author}",
                colour=target.colour,
                timestamp=dt.utcnow()
            )

            emb.add_field(name='Reason', value=reason, inline=False)
            emb.set_footer(text=f"ID: {target.id}", icon_url=target.avatar_url)

            await log_channel(self.bot, ctx.guild).send(
                embed=emb
            )

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user, *, reason=None):
        """
        Bans a member. Requires the ban_member permission
        """
        if not reason:
            reason = "Unspecified"
        try:
            target = await commands.MemberConverter().convert(ctx, user)
            await target.send(f"You were banned from {ctx.guild} for reason: {reason}")
            await target.ban(reason=reason)
        except (commands.BadArgument, discord.Forbidden) as error:
            if isinstance(error, commands.BadArgument):
                return await ctx.send("Member not found. Try mentioning them (or they left)")
        else:
            emb = discord.Embed(
                title='Member Banned',
                description=f"Name: {target}\nExecuted by: {ctx.author}",
                colour=target.colour,
                timestamp=dt.utcnow()
            )

            emb.add_field(name='Reason', value=reason, inline=False)
            emb.set_footer(text=f"ID: {target.id}", icon_url=target.avatar_url)

            await log_channel(self.bot, ctx.guild).send(
                embed=emb
            )