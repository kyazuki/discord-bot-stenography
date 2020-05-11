import asyncio
import glob
import logging
import os
import re

from discord.ext import commands
import discord

from settings import audio_suffix
from settings import bot_name
from settings import Data
from settings import EXTENSIONS
from settings import logfile
from settings import Messages
from settings import token

class discordBot(commands.Bot):
    """commands.Botを継承するクラス。
    ログの生成や、起動時/終了時の処理を記述するために自作している。
    最終的にはcommands.Botが呼び出される
    """
    def __init__(self, bot_name):
        """インスタンスを生成すると最初に呼び出される関数。
        """
        # bot_nameを取得
        self.bot_name = bot_name

        # ログのファイル名を設定
        self.logfile = logfile.format(bot_name)

        # ログの生成
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=self.logfile, encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        
        # Dataクラスのインスタンスを作成
        self.data = Data(self.bot_name)

        # 現バージョンを取得
        with open('./changelog.txt', mode = 'r', encoding = 'UTF-8') as f:
            self.version = re.match(r'v[0-9]+.[0-9]+.[0-9]+', f.readline()).group()

        # commands.Botに丸投げ
        super().__init__(self.check_prefix, help_command=None)

        # cogsフォルダ直下の.pyファイルを読み込み
        for cog in EXTENSIONS:
            self.load_extension(cog)

    # 各Botのプレフィックスを提示する関数
    # commands.Botに代入する用
    def check_prefix(self, bot, message):
        guild = message.guild
        if guild:
            return self.data.guild_prefix.get(guild.id, self.data.default_prefix)
        else:
            return self.data.default_prefix
    
    # 各箇所で使用する用
    def _get_prefix(self, ctx):
        guild = ctx.guild
        if guild:
            return self.data.guild_prefix.get(guild.id, self.data.default_prefix)[0]
        else:
            return self.data.default_prefix
    
    async def on_ready(self):
        """Bot起動時に呼び出される関数。
        コンソールにbot_nameとアカウント名を表示し、
        Discordのアクティビティを Type helpをプレイ中に設定。
        指定されたチャンネルに再起動した旨をメッセージ送信。
        """
        print('{0.bot_name}: Logged in as {0.user}'.format(self))
        await self.change_presence(activity = discord.Game(self.version))
    
    async def on_message(self, message):
        """Botがいるチャンネルで、メッセージが送られると呼び出される関数
        """
        # 自分のメッセージならスルーして終了
        if message.author == self.user:
            return

        # Botのメッセージならスルーして終了
        if message.author.bot:
            return

        if 'するめ' in message.content:
            await message.channel.send('するめではなくあたりめです')
        
        # 残りはcommands.Botに丸投げ 
        return await super().on_message(message)
    
    async def on_command_error(self, context, exception):
        """Botのコマンドでエラーが起きたときに呼び出される関数
        """
        # guild_onlyが指定されているコマンドをDMで送られたときに起こるエラー
        if isinstance(exception, commands.NoPrivateMessage):
            await context.send(Messages.check_guild_only)
        # has_permissionが指定されているコマンドを、権限のない人が使用したときに起こるエラー
        elif isinstance(exception, commands.MissingPermissions):
            await context.send(Messages.check_missing_permission)
        # 存在しないコマンドを送られたときに起こるエラー
        elif isinstance(exception, commands.CommandNotFound):
            # passは何もしない
            pass
        # 残りはcommands.Botに丸投げ
        else:
            return await super().on_command_error(context, exception)

    async def on_disconnect(self):
        """Bot終了時に呼び出される関数。
        コンソールにbot_nameとアカウント名を表示するだけ
        """
        print('{0.bot_name}: Logged out as {0.user}'.format(self))

# importとかではなく, python discordbot.pyのように直接このファイルが実行されたら以下を処理
if __name__ == '__main__':
    
    # 各Botをスタートさせる
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(discordBot(bot_name[i]).start(token[i])) for i in range(len(bot_name))]
    gathered = asyncio.gather(*tasks, loop = loop)
    loop.run_until_complete(gathered)

    # Botが全て終了されるとここにくる
    # ダウンロードした音声ファイルを全削除
    for path in glob.glob('*.' + audio_suffix):
        if os.path.isfile(path):
            os.remove(path)
