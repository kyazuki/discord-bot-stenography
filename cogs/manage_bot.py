from discord.ext import commands

from settings import DEVELOPERS_ID
from settings import EXTENSIONS
from settings import guild_prefix
from settings import Messages

class manage_bot(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.check(lambda ctx: not ctx.author.bot)
    async def check_prefix(self, ctx):
        await ctx.send(Messages['prefix_show'].format(', '.join(guild_prefix[self.bot.bot_name][ctx.guild.id])))
    @check_prefix.error
    async def check_prefix_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, KeyError):
                await ctx.send(Messages['prefix_not_found'])
            else:
                raise
        else:
            raise
    
    @commands.command()
    @commands.guild_only()
    @commands.check(lambda ctx: not ctx.author.bot)
    async def set_prefix(self, ctx, *, prefixes=''):
        if prefixes.split():
            guild_prefix[self.bot.bot_name][ctx.guild.id] = prefixes.split()
            await ctx.send(Messages['prefix_set'])
        else:
            del guild_prefix[self.bot.bot_name][ctx.guild.id]
            await ctx.send(Messages['prefix_delete'])
    @set_prefix.error
    async def set_prefix_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, KeyError):
                await ctx.send(Messages['prefix_not_found'])
            else:
                raise
        else:
            raise

    @commands.command()
    @commands.check(lambda ctx: ctx.author.id in DEVELOPERS_ID)
    async def reload(self, ctx):
        for cog in EXTENSIONS:
            self.bot.reload_extension(cog)
        await ctx.send(Messages['reload'])
    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(Messages['check_not_developer'])
        else:
            raise

    @commands.command()
    @commands.check(lambda ctx: ctx.author.id in DEVELOPERS_ID)
    async def close(self, ctx):
        await self.bot.close()
    @close.error
    async def close_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(Messages['check_not_developer'])
        else:
            raise

def setup(bot):
    bot.add_cog(manage_bot(bot))