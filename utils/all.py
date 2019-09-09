import aiohttp
import datetime
import discord


# Colours
class Colours:
    msg_delete = 0x000000
    msg_edit = 0xffffff
    channel_creation = 0x0900ff
    channel_deletion = 0x030054
    channel_update = 0x8480ff
    member_update = 0x00ff00
    member_ban = 0xff0000
    member_unban = 0xfc06c2
    member_join = 0x645ebc
    member_leave = 0xcacaca
    server_update = 0xf7ff00


colours = Colours()


# Logging
def log_channel(bot, guild):
    res = bot.fetch(
        "SELECT log_channel FROM guild_info WHERE guild_id={}"
            .format(guild.id)
    )
    if not res:
        return None
    channel = guild.get_channel(int(res[0]))
    return channel


def embed_from_dict(title, colour, content: dict, footer: tuple = False):
    emb = discord.Embed(
        title=title,
        colour=colour,
        timestamp=datetime.datetime.utcnow()
    )
    for key in content.keys():
        emb.add_field(
            name=key,
            value=content[key],
            inline=False
        )
    if footer:
        empty = discord.Embed.Empty
        emb.set_footer(
            text=str(footer[0]) if footer[0] else empty,
            icon_url=str(footer[1]) if footer[1] else empty
        )
    return emb


# Web requests
async def post_hastebin(content):
    content = content.encode('utf-8')

    async with aiohttp.ClientSession() as ses:
        async with ses.post("https://hastebin.com/documents", data=content) as post:
            code = (await post.json())["key"]  # Get the URL code
    complete_url = f"https://hastebin.com/{code}"

    return complete_url
