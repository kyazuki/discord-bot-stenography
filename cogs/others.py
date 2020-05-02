import asyncio
import re

from discord.ext import commands
import discord

from settings import DEVELOPERS_ID
from settings import logfile
from settings import Messages
from settings import neko_channel_id

class others(commands.Cog):
    """ 分類し難いコマンドをまとめたクラス
    """
    def __init__(self, bot):
        self.bot = bot

    # /neko
    @commands.command()
    async def neko(self, ctx):
        await ctx.send(Messages['neko1'])
        await self.bot.get_channel(neko_channel_id).send(Messages['neko2'])
    
    # /guild_name
    @commands.command()
    @commands.guild_only()
    async def guild_name(self, ctx):
        await ctx.send(Messages['guild_name'].format(ctx.guild.name))

    # /changelog [all | 表示上限数]
    @commands.command()
    async def changelog(self, ctx, max_num = '1'):
        match_pattern = re.match(r'[0-9]+', max_num)
        max = None
        if max_num == 'all' or match_pattern:
            if match_pattern:
                max = int(max_num)
            else:
                max = -1

        if max:
            desc = ''
            with open('./changelog.txt', mode = 'r', encoding = 'UTF-8') as f:
                count = 0
                for line in f:
                    if re.match(r'v[0-9]+.[0-9]+.[0-9]+:', line):
                        count += 1
                    if max != -1 and count > max:
                        break
                    desc += line
            embed = discord.Embed(title='Change Log', description=desc)
            await ctx.send(embed = embed)
        else:
            await ctx.send(Messages['changelog_bad_argument'])
    
    # /log
    @commands.command()
    @commands.check(lambda ctx: ctx.author.id in DEVELOPERS_ID)
    async def log(self, ctx):
        await ctx.send(Messages['log_send'], file=discord.File(logfile[self.bot.bot_name]))
    @log.error
    async def log_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(Messages['check_not_developer'])
        else:
            raise
    
    # /delete <削除件数>
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages = True)
    async def delete(self, ctx, limit: int):
        m = await ctx.send(Messages['delete_confirm'].format(limit))
        def check(m):
            return re.fullmatch(r'[yn]', m.content) and m.channel == ctx.channel and m.author == ctx.author
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 30.0)
        except asyncio.TimeoutError:
            await m.edit(content=Messages['timeout'], embed=None)
        else:
            if msg.content == 'y':
                await msg.delete()
                await m.delete()
                await ctx.message.delete()
                async for m in ctx.history(limit = limit):
                    await m.delete()
    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.MissingPermissions):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(Messages['delete_missing_argument'])
        elif isinstance(error, commands.BadArgument):
            await ctx.send(Messages['delete_bad_argument'])
        else:
            raise


def setup(bot):
    bot.add_cog(others(bot))