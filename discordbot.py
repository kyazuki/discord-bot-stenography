import asyncio
import glob
import logging
import os

from discord.ext import commands
import discord

from settings import audio_suffix_name
from settings import bot_name
from settings import check_prefix
from settings import EXTENSIONS
from settings import logfile
from settings import Messages
from settings import token

class discordBot(commands.Bot):

    def __init__(self, command_prefix, bot_name):
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=logfile[bot_name], encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        
        super().__init__(command_prefix, help_command=None)

        self.bot_name = bot_name

        for cog in EXTENSIONS:
            self.load_extension(cog)

    async def on_ready(self):
        print('{0.bot_name}: Logged in as {0.user}'.format(self))
        await self.change_presence(activity = discord.Game('Type help'))
        # await self.get_channel(703931482275709038).send('Botが再起動しました')
    
    async def on_message(self, message):
        if message.author == self.user:
            return

        if 'help' in message.content:
            embed = discord.Embed(title='コマンド一覧')
            embed.add_field(name='/play <検索ワード>', value='<検索ワード>を含む音声ファイルを再生します', inline=False)
            embed.add_field(name='/randomplay <検索ワード>', value='<検索ワード>を含む音声ファイルの中からランダムに1つ再生します', inline=False)
            embed.add_field(name='/seek <開始秒数> [検索ワード]', value='<検索ワード>を含む音声ファイルを指定された秒数から再生します', inline=False)
            embed.add_field(name='/pause', value='再生を一時停止/再開します', inline=False)
            embed.add_field(name='/stop', value='再生を終了します', inline=False)
            embed.add_field(name='/volume <0.0から1.0までの小数点>', value='音量を調整します', inline=False)
            embed.add_field(name='/disconnect', value='ボイスチャンネルから切断します', inline=False)
            embed.add_field(name='/neko', value='にゃーん', inline=False)
            if message.guild:
                name = message.guild.get_member(self.user.id).nick
            else:
                name = self.user.name
            embed.set_author(name=name, url=self.user.avatar_url_as(static_format='png', size=128), icon_url=self.user.avatar_url_as(static_format='png', size=128))
            await message.channel.send(embed = embed)

        if 'するめ' in message.content:
            await message.channel.send('するめではなくあたりめです')
        
        return await super().on_message(message)
    
    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.NoPrivateMessage):
            await context.send(Messages['check_guild_only'])
        elif isinstance(exception, commands.MissingPermissions):
            await context.send(Messages['check_missing_permission'])
        elif isinstance(exception, commands.CommandNotFound):
            pass
        else:
            return await super().on_command_error(context, exception)
    
    async def on_disconnect(self):
        print('{0.bot_name}: Logged out as {0.user}'.format(self))
    
if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(discordBot(check_prefix, bot_name[i]).start(token[i])) for i in range(len(bot_name))]
    gathered = asyncio.gather(*tasks, loop = loop)
    loop.run_until_complete(gathered)

    for path in glob.glob('*' + audio_suffix_name):
        if os.path.isfile(path):
            os.remove(path)
