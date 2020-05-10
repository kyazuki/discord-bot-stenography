from discord.ext import commands
import discord

from settings import alias
from settings import get_prefix

class help_command(commands.Cog):
    """ helpコマンド系をまとめたクラス
    """
    def __init__(self, bot):
        self.bot = bot

    # /help
    @commands.command(aliases=alias.help)
    async def help(self, ctx):
        embed = discord.Embed(title='コマンド一覧')
        embed.add_field(name=get_prefix(self.bot, ctx)+'play <検索ワード>', value='<検索ワード>を含む音声ファイルを再生します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'replay', value='前回再生した音声ファイルを再生します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'randomplay <検索ワード>', value='<検索ワード>を含む音声ファイルの中からランダムに1つ再生します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'seek <開始秒数> [検索ワード]', value='<検索ワード>を含む音声ファイルを指定された秒数から再生します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'pause', value='再生を一時停止します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'resume', value='再生を再開します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'stop', value='再生を終了します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'search <検索ワード>', value='<検索ワード>を含む音声ファイルを検索します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'volume <0.0から1.0までの小数点>', value='音量を調整します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'connect', value='ボイスチャンネルに接続します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'disconnect', value='ボイスチャンネルから切断します', inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'neko', value='にゃーん', inline=False)
        if ctx.guild:
            name = ctx.guild.me.display_name
        else:
            name = self.bot.user.name
        embed.set_author(name=name, url=self.bot.user.avatar_url_as(static_format='png', size=128), icon_url=self.bot.user.avatar_url_as(static_format='png', size=128))
        await ctx.send(embed = embed)

    # /alias
    @commands.command(aliases=alias.alias)
    async def alias(self, ctx):
        embed = discord.Embed(title='エイリアス一覧')
        embed.add_field(name=get_prefix(self.bot, ctx)+'play', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.play)), inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'replay', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.replay)), inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'randomplay', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.randomplay)), inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'seek', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.seek)), inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'search', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.search)), inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'connect', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.connect)), inline=False)
        embed.add_field(name=get_prefix(self.bot, ctx)+'disconnect', value=', '.join(map(lambda s: get_prefix(self.bot, ctx) + s, alias.disconnect)), inline=False)
        if ctx.guild:
            name = ctx.guild.me.display_name
        else:
            name = self.bot.user.name
        embed.set_author(name=name, url=self.bot.user.avatar_url_as(static_format='png', size=128), icon_url=self.bot.user.avatar_url_as(static_format='png', size=128))
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(help_command(bot))
