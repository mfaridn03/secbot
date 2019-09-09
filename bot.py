import asyncio
import sqlite3
import traceback

import discord

from discord.ext import commands

TOKEN = "NTk1ODY1Mzg2NTc5Mzk0NTcx.XRxNGA.kZycAv3XZG9jYvD6YmSHcKoNch8"
# Token will be refreshed
modules = [
    'cogs.server',
    'cogs.chatlogger',
    'cogs.captcha',
    'jishaku'
]


class BotBase(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='s!',
            reconnect=True,
            case_insensitive=True,
            fetch_offline_members=True,
            status=discord.Status.idle,
            activity=discord.Game(
                name='booting up...'
            )
        )
        # DB init
        self.conn = sqlite3.connect('server_security.db')
        self.cursor = self.conn.cursor()
        # shortcuts
        self.commit = self.conn.commit
        self.execute = self.cursor.execute
        self.fetch = self.fetchone
        # Admin stuff
        self.owner = 191036924570501120

    def fetchone(self, query):
        res = self.cursor.execute(query)
        return res.fetchone()

    async def start(self):
        for m in modules:  # Load modules from local folders
            try:
                self.load_extension(m)
                print(m, 'loaded.')
            except:  # In case of error within module
                print(traceback.format_exc())
        print('---')
        await super().start(TOKEN)

    def init_db(self):
        self.execute(
            "DROP TABLE IF EXISTS guild_info"
        )
        self.execute(
            "CREATE TABLE IF NOT EXISTS guild_info(guild_id NUMERIC, \
            security_type SMALLINT, log_channel INTEGER, \
            unverified_role INTEGER, verified_role INTEGER, word_filter TEXT)"
        )
        self.commit()
        print("Database initialised")

    async def on_ready(self):
        self.init_db()
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                name=f'over {len(self.guilds)} servers',
                type=discord.ActivityType.watching
            )
        )
        print('Logged in!\n')
        print(str(self.user))
        print(str(self.user.id), '\n')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.lower().startswith("s!") and not message.guild:
            return await message.author.send("No commands in DMs")

        await self.process_commands(message)

    @staticmethod
    def split_text(text: str, length: int = 1900):
        return [text[i:i + length] for i in range(0, len(text), length)]

    async def on_error(self, event_method, *args, **kwargs):
        emb = discord.Embed(title='Error')
        emb.description = f"```py\n{traceback.format_exc()}\n```"
        await self.get_user(self.owner).send(embed=emb)


if __name__ == '__main__':
    BotBase().run()
