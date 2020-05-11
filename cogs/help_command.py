from discord.ext import commands
import discord

from settings import Alias

class help_command(commands.Cog):
    """ helpコマンド系をまとめたクラス
    """
    def __init__(self, bot):
        self.bot = bot

    # /help
    @commands.command(aliases=Alias.help)
    async def help(self, ctx):
        prefix = self.bot._get_prefix(ctx)
        embed = discord.Embed(title='コマンド一覧')
        embed.add_field(name=prefix+'play <検索ワード>', value='<検索ワード>を含む音声ファイルを再生します', inline=False)
        embed.add_field(name=prefix+'replay', value='前回再生した音声ファイルを再生します', inline=False)
        embed.add_field(name=prefix+'randomplay <検索ワード>', value='<検索ワード>を含む音声ファイルの中からランダムに1つ再生します', inline=False)
        embed.add_field(name=prefix+'seek <開始秒数> [検索ワード]', value='<検索ワード>を含む音声ファイルを指定された秒数から再生します', inline=False)
        embed.add_field(name=prefix+'pause', value='再生を一時停止します', inline=False)
        embed.add_field(name=prefix+'resume', value='再生を再開します', inline=False)
        embed.add_field(name=prefix+'stop', value='再生を終了します', inline=False)
        embed.add_field(name=prefix+'search <検索ワード>', value='<検索ワード>を含む音声ファイルを検索します', inline=False)
        embed.add_field(name=prefix+'volume <0.0から1.0までの小数点>', value='音量を調整します', inline=False)
        embed.add_field(name=prefix+'connect', value='ボイスチャンネルに接続します', inline=False)
        embed.add_field(name=prefix+'disconnect', value='ボイスチャンネルから切断します', inline=False)
        embed.add_field(name=prefix+'neko', value='にゃーん', inline=False)
        if ctx.guild:
            name = ctx.guild.me.display_name
        else:
            name = self.bot.user.name
        embed.set_author(name=name, url=self.bot.user.avatar_url_as(static_format='png', size=128), icon_url=self.bot.user.avatar_url_as(static_format='png', size=128))
        await ctx.send(embed = embed)

    # /alias
    @commands.command(aliases=Alias.alias)
    async def alias(self, ctx):
        prefix = self.bot._get_prefix(ctx)
        embed = discord.Embed(title='エイリアス一覧')
        embed.add_field(name=prefix+'play', value=', '.join(map(lambda s: prefix + s, Alias.play)), inline=False)
        embed.add_field(name=prefix+'replay', value=', '.join(map(lambda s: prefix + s, Alias.replay)), inline=False)
        embed.add_field(name=prefix+'randomplay', value=', '.join(map(lambda s: prefix + s, Alias.randomplay)), inline=False)
        embed.add_field(name=prefix+'seek', value=', '.join(map(lambda s: prefix + s, Alias.seek)), inline=False)
        embed.add_field(name=prefix+'search', value=', '.join(map(lambda s: prefix + s, Alias.search)), inline=False)
        embed.add_field(name=prefix+'connect', value=', '.join(map(lambda s: prefix + s, Alias.connect)), inline=False)
        embed.add_field(name=prefix+'disconnect', value=', '.join(map(lambda s: prefix + s, Alias.disconnect)), inline=False)
        if ctx.guild:
            name = ctx.guild.me.display_name
        else:
            name = self.bot.user.name
        embed.set_author(name=name, url=self.bot.user.avatar_url_as(static_format='png', size=128), icon_url=self.bot.user.avatar_url_as(static_format='png', size=128))
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(help_command(bot))
