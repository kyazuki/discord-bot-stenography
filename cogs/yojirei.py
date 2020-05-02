from discord.ext import commands

from settings import Messages
from yojirei_bot import text_analysis

class yojirei(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['y'])
    @commands.check(lambda ctx: not ctx.author.bot)
    async def yojirei(self, ctx, word):
        try:
            index, yojirei, tip = text_analysis.execute(text_analysis.Mode.SEARCH, '"{}"'.format(word))
        except KeyError:
            await ctx.send(Messages['yojirei_not_found'].format(index))
        else:
            await ctx.send(Messages['yojirei_show'].format(yojirei, tip))
    @yojirei.error
    async def yojirei_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(Messages['yojirei_missing_argument'])
        else:
            raise

def setup(bot):
    bot.add_cog(yojirei(bot))