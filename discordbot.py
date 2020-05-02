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
    """commands.Botを継承するクラス。
    ログの生成や、起動時/終了時の処理を記述するために自作している。
    最終的にはcommands.Botが呼び出される
    """
    def __init__(self, command_prefix, bot_name):
        """インスタンスを生成すると最初に呼び出される関数。
        """
        # ログの生成
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=logfile[bot_name], encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        
        # commands.Botに丸投げ
        super().__init__(command_prefix, help_command=None)

        # bot_nameを取得
        self.bot_name = bot_name

        # cogsフォルダ直下の.pyファイルを読み込み
        for cog in EXTENSIONS:
            self.load_extension(cog)

    async def on_ready(self):
        """Bot起動時に呼び出される関数。
        コンソールにbot_nameとアカウント名を表示し、
        Discordのアクティビティを Type helpをプレイ中に設定。
        指定されたチャンネルに再起動した旨をメッセージ送信。
        """
        print('{0.bot_name}: Logged in as {0.user}'.format(self))
        await self.change_presence(activity = discord.Game('Type help'))
        # await self.get_channel(703931482275709038).send('Botが再起動しました')
    
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
    tasks = [loop.create_task(discordBot(check_prefix, bot_name[i]).start(token[i])) for i in range(len(bot_name))]
    gathered = asyncio.gather(*tasks, loop = loop)
    loop.run_until_complete(gathered)

    # Botが全て終了されるとここにくる
    # ダウンロードした音声ファイルを全削除
    for path in glob.glob('*' + audio_suffix_name):
        if os.path.isfile(path):
            os.remove(path)
