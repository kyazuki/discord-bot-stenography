from discord.ext import commands
import discord

class help_command(commands.Cog):
    """ helpコマンド系をまとめたクラス
    """
    def __init__(self, bot):
        self.bot = bot

    # /help
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title='コマンド一覧')
        embed.add_field(name='/play <検索ワード>', value='<検索ワード>を含む音声ファイルを再生します', inline=False)
        embed.add_field(name='/replay', value='前回再生した音声ファイルを再生します', inline=False)
        embed.add_field(name='/randomplay <検索ワード>', value='<検索ワード>を含む音声ファイルの中からランダムに1つ再生します', inline=False)
        embed.add_field(name='/seek <開始秒数> [検索ワード]', value='<検索ワード>を含む音声ファイルを指定された秒数から再生します', inline=False)
        embed.add_field(name='/pause', value='再生を一時停止します', inline=False)
        embed.add_field(name='/resume', value='再生を再開します', inline=False)
        embed.add_field(name='/stop', value='再生を終了します', inline=False)
        embed.add_field(name='/search <検索ワード>', value='<検索ワード>を含む音声ファイルを検索します', inline=False)
        embed.add_field(name='/volume <0.0から1.0までの小数点>', value='音量を調整します', inline=False)
        embed.add_field(name='/connect', value='ボイスチャンネルに接続します', inline=False)
        embed.add_field(name='/disconnect', value='ボイスチャンネルから切断します', inline=False)
        embed.add_field(name='/neko', value='にゃーん', inline=False)
        if ctx.guild:
            name = ctx.guild.get_member(self.bot.user.id).nick
        else:
            name = self.bot.user.name
        embed.set_author(name=name, url=self.bot.user.avatar_url_as(static_format='png', size=128), icon_url=self.bot.user.avatar_url_as(static_format='png', size=128))
        await ctx.channel.send(embed = embed)

    # /alias
    @commands.command()
    async def alias(self, ctx):
        embed = discord.Embed(title='エイリアス一覧')
        embed.add_field(name='/play', value='/p', inline=False)
        embed.add_field(name='/replay', value='/rp', inline=False)
        embed.add_field(name='/randomplay', value='/rndp', inline=False)
        embed.add_field(name='/seek', value='/sk', inline=False)
        embed.add_field(name='/search', value='/s', inline=False)
        embed.add_field(name='/connect', value='/c', inline=False)
        embed.add_field(name='/disconnect', value='/dc', inline=False)
        if ctx.guild:
            name = ctx.guild.get_member(self.bot.user.id).nick
        else:
            name = self.bot.user.name
        embed.set_author(name=name, url=self.bot.user.avatar_url_as(static_format='png', size=128), icon_url=self.bot.user.avatar_url_as(static_format='png', size=128))
        await ctx.channel.send(embed = embed)

def setup(bot):
    bot.add_cog(help_command(bot))