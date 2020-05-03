from discord.ext import commands
import discord

from settings import alias
from settings import Messages

class voice_client(commands.Cog):
    """ ボイスチャンネル系のコマンドをまとめたクラス
    """
    def __init__(self, bot):
        self.bot = bot

    # /connect
    @commands.command(aliases=alias.connect)
    @commands.guild_only()
    async def connect(self, ctx):
        await ctx.author.voice.channel.connect()
        await ctx.send(Messages.voicechannel_connected)
    @connect.error
    async def connect_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.ClientException):
                if ctx.author.voice.channel == ctx.guild.voice_client.channel:
                    await ctx.send(Messages.voicechannel_already_connected)
                else:
                    await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
            elif isinstance(error.original, AttributeError):
                await ctx.send(Messages.voicechannel_not_connect)
            else:
                raise
        else:
            raise
    
    # /disconnect
    @commands.command(aliases=alias.disconnect)
    @commands.guild_only()
    async def disconnect(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await ctx.send(Messages.voicechannel_disconnected)
    @disconnect.error
    async def disconnect_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, AttributeError):
                await ctx.send(Messages.voicechannel_not_connect_bot)
            else:
                raise
        else:
            raise

def setup(bot):
    bot.add_cog(voice_client(bot))
