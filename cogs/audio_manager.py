import asyncio
import os
import random
import re
import time

from discord.ext import commands
import discord

from settings import alias
from settings import audio_start_time
from settings import audio_suffix
from settings import audio_erapsed_time
from settings import drive
from settings import get_prefix
from settings import Messages
from settings import pause_method
from settings import randomfile

class audio_manager(commands.Cog):
    """ 音声ファイル関連のコマンドをまとめたクラス
    """
    def __init__(self, bot):
        self.bot = bot

    def search_audio_in_drive(self, search_words):
        """引数に受けた文字列リストの要素をタイトルに全て含む、ドライブの音声ファイルのリストを返します"""
        query = 'mimeType contains "audio/"'
        for word in search_words:
            query += ' and title contains "{}"'.format(word)
        return drive.ListFile({'q': query}).GetList()
    
    def embed_audio_list(self, search_words, fileList, author, choosable=False):
        """ドライブのファイルのリストを一覧にしたdiscord.Embedを返します
        
        オプション引数としてTrueを受け取ると、
        Embedの最後尾に'数字をタイプしてください'の旨のメッセージを付け加えます
        """
        title = 'Search: ' + ', '.join(search_words)
        desc = ''
        count = 0
        for f in fileList:
            count += 1
            desc += '`{}.` {}\n\n'.format(count, f['title'])
            if count >= 10:
                break
        if choosable:
            desc += Messages.choice_number
        embed = discord.Embed(title=title, description=desc)
        embed.set_author(name=author.display_name, url=author.avatar_url_as(static_format='png', size=128), icon_url=author.avatar_url_as(static_format='png', size=128))
        full_pages = len(fileList) // 10
        if len(fileList) % 10:
            full_pages += 1
        embed.set_footer(text='page 1/{}'.format(full_pages))
        return embed

    async def choice_audio(self, search_words, fileList, guild, channel, author, offset = 0):
        """ドライブのファイルのリストを一覧にしたEmbedメッセージを送信し、
        数字がタイプされると対応したファイルを再生します

        オプション引数として整数値を受け取ると、
        その秒数から音声ファイルを再生します
        """
        embed = self.embed_audio_list(search_words, fileList, author, True)
        m = await channel.send(embed = embed)
        if len(fileList) > 10:
            await m.add_reaction('◀️')
            await m.add_reaction('▶️')
        def check(m):
            return re.fullmatch(r'[0-9]+', m.content) and m.channel == channel
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 30.0)
        except asyncio.TimeoutError:
            await m.edit(content=Messages.timeout, embed=None)
        else:
            try:
                file = fileList[int(msg.content) - 1]
            except IndexError:
                await m.edit(content=Messages.invalid_value, embed=None)
            else:
                await m.edit(content=Messages.choosed_audio.format(file['title']), embed=None)
                await self.play_audio(file, guild, channel, author, offset, self.after_play_audio)
        finally:
            await m.clear_reactions()

    async def play_audio(self, file, guild, channel, author, offset = 0, after = None):
        """引数に受けたファイルを再生します

        オプション引数として整数値を受け取ると、
        その秒数から音声ファイルを再生します
        また、関数を受け取ると、
        再生が終わるか、例外によって中断されたときにその関数を実行します
        """
        await channel.send(Messages.audio_play_before.format(file['title']))
        
        file_object = drive.CreateFile({'id': file['id']})

        m = await channel.send(Messages.download_started)
        filename = str(guild.id) + audio_suffix[self.bot.bot_name]
        file_object.GetContentFile(filename)
        await m.edit(content=Messages.download_finished)

        audio_source = discord.FFmpegPCMAudio(filename if offset == 0 else filename, options = '-ss ' + str(offset))
        audio_source = discord.PCMVolumeTransformer(audio_source)

        if offset == 0:
            await m.edit(content=Messages.audio_play)
        else: 
            await m.edit(content=Messages.audio_play_seek.format(offset // 60, offset % 60))

        voice_client = guild.voice_client
        if voice_client and voice_client.is_playing:
            voice_client.stop()

        if not voice_client:
            voice_client = await discord.VoiceChannel.connect(author.voice.channel)
        elif voice_client.channel != author.voice.channel:
            await voice_client.move_to(author.voice.channel)
        voice_client.play(audio_source, after=after)
        audio_start_time[self.bot.bot_name][guild.id] = time.perf_counter()
        audio_erapsed_time[self.bot.bot_name][guild.id] = offset

    def after_play_audio(self, error):
        """音声ファイルが再生終了したときに呼び出される関数です
        """
        if error:
            raise error

    # /play <検索ワード> 
    @commands.command(aliases=alias.play)
    @commands.guild_only()
    async def play(self, ctx, *args):
        if ctx.author.voice is None or ctx.author.voice.afk:
            await ctx.send(Messages.voicechannel_not_connect)
            return

        if not args:
            voice_client = ctx.guild.voice_client
            if voice_client and voice_client.is_paused():
                if not ctx.guild.id in pause_method:
                   pause_method[self.bot.bot_name][ctx.guild.id] = 'None'
                
                if pause_method[self.bot.bot_name][ctx.guild.id] == 'stop':
                    await ctx.send(Messages.suggest_replay.format(get_prefix(self.bot, ctx)))
                else:
                    await ctx.send(Messages.suggest_resume.format(get_prefix(self.bot, ctx)))
            else:
                await ctx.send(Messages.play_missing_argument.format(get_prefix(self.bot, ctx)))
            
            return
        
        fileList = self.search_audio_in_drive(args)
        await ctx.send(Messages.file_count.format(len(fileList)))
        
        if len(fileList) >= 2:
            await self.choice_audio(args, fileList, ctx.guild, ctx.channel, ctx.author)
        elif len(fileList) == 1:
            await self.play_audio(fileList[0], ctx.guild, ctx.channel, ctx.author, after = self.after_play_audio)
        elif len(fileList) <= 0:
            await ctx.send(Messages.file_not_found)            

    # /replay
    @commands.command(aliases=alias.replay)
    @commands.guild_only()
    async def replay(self, ctx):
        if ctx.author.voice is None or ctx.author.voice.afk:
            await ctx.send(Messages.voicechannel_not_connect)
            return
        
        filename = str(ctx.guild.id) + audio_suffix[self.bot.bot_name]
        if os.path.isfile(filename):
            await ctx.send(Messages.replay)
            audio_source = discord.FFmpegPCMAudio(filename)
            audio_source = discord.PCMVolumeTransformer(audio_source)

            voice_client = ctx.guild.voice_client
            if not voice_client:
                voice_client = await discord.VoiceChannel.connect(ctx.author.voice.channel)
            elif voice_client.channel != ctx.author.voice.channel:
                await voice_client.move_to(ctx.author.voice.channel)
            
            if voice_client and voice_client.is_playing:
                voice_client.stop()
            voice_client.play(audio_source, after=self.after_play_audio)
            audio_start_time[self.bot.bot_name][guild.id] = time.perf_counter()
            audio_erapsed_time[self.bot.bot_name][guild.id] = 0
        else:
            await ctx.send(Messages.replay_nofile.format(get_prefix(self.bot, ctx)))
    
    # /randomplay [検索ワード]
    @commands.command(aliases=alias.randomplay)
    @commands.guild_only()
    async def randomplay(self, ctx, *args):
        if ctx.author.voice is None or ctx.author.voice.afk:
            await ctx.send(Messages.voicechannel_not_connect)
            return
        
        if args:
            randomfile[self.bot.bot_name][ctx.guild.id] = self.search_audio_in_drive(args)
                
            if len(randomfile[self.bot.bot_name][ctx.guild.id]) >= 1:
                search_word = args
                await self.play_audio(random.choice(randomfile[self.bot.bot_name][ctx.guild.id]), ctx.guild, ctx.channel, ctx.author, after = self.after_play_audio)
            elif len(randomfile[self.bot.bot_name][ctx.guild.id]) <= 0:
                await ctx.send(Messages.file_not_found)
        else:
            if ctx.guild.id in randomfile:
                await self.play_audio(random.choice(randomfile[self.bot.bot_name][ctx.guild.id]), ctx.guild, ctx.channel, ctx.author, after = self.after_play_audio)
            else:
                await ctx.send(Messages.random_nofile.format(get_prefix(self.bot, ctx)))

    # /seek <開始秒数> [検索ワード]
    @commands.command(aliases=alias.seek)
    @commands.guild_only()
    async def seek(self, ctx, time, *args):
        if ctx.author.voice is None or ctx.author.voice.afk:
            await ctx.send(Messages.voicechannel_not_connect)
            return
        
        match_pattern_1 = re.fullmatch(r'[0-9]+', time)
        match_pattern_2 = re.fullmatch(r'([0-9]+):([0-5][0-9])', time)
        if match_pattern_1 or match_pattern_2:
            if match_pattern_1:
                offset = int(time)
            elif match_pattern_2:
                offset = int(match_pattern_2.groups()[0]) * 60 + int(match_pattern_2.groups()[1])

            if not args:
                voice_client = ctx.guild.voice_client
                if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
                    filename = str(ctx.guild.id) + audio_suffix[self.bot.bot_name]
                    audio_source = discord.FFmpegPCMAudio(filename, options='-ss ' + str(offset))
                    audio_source = discord.PCMVolumeTransformer(audio_source)
                    voice_client.source = audio_source
                    await ctx.send(Messages.seek_start.format(offset // 60, offset % 60))
                else:
                    await ctx.send(Messages.seek_not_playing.format(get_prefix(self.bot, ctx)))
            else:
                fileList = self.search_audio_in_drive(args)
                await ctx.send(Messages.file_count.format(len(fileList)))
                
                if len(fileList) >= 2:
                    await self.choice_audio(args, fileList, ctx.guild, ctx.channel, ctx.author, offset)
                elif len(fileList) == 1:
                    await self.play_audio(fileList[0], ctx.guild, ctx.channel, ctx.author, offset, self.after_play_audio)
                elif len(fileList) <= 0:
                    await ctx.send(Messages.file_not_found)
        else:
            await ctx.send(Messages.seek_bad_argument)
    @seek.error
    async def seek_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(Messages.seek_missing_argument.format(self.bot, ctx))
        else:
            raise
    
    # /pause
    @commands.command(aliases=alias.pause)
    @commands.guild_only()
    async def pause(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                audio_erapsed_time[self.bot.bot_name][ctx.guild.id] += time.perf_counter() - audio_start_time[self.bot.bot_name][ctx.guild.id]
                await ctx.send(Messages.audio_pause + ' ' + Messages.audio_erapsed_time.format(int(audio_erapsed_time[self.bot.bot_name][ctx.guild.id]) // 60, int(audio_erapsed_time[self.bot.bot_name][ctx.guild.id]) % 60))
                pause_method[self.bot.bot_name][ctx.guild.id] = 'pause'
                voice_client.pause()
            elif voice_client.is_paused():
                if not ctx.guild.id in pause_method:
                   pause_method[self.bot.bot_name][ctx.guild.id] = 'None'
                
                if pause_method[self.bot.bot_name][ctx.guild.id] == 'pause':
                    audio_start_time[self.bot.bot_name][ctx.guild.id] = time.perf_counter()
                    await ctx.send(Messages.audio_resume)
                    voice_client.resume()
                else:
                    await ctx.send(Messages.audio_not_playing + '\n' + Messages.suggest_resume_and_stop.format(get_prefix(self.bot, ctx)))
            else:
                await ctx.send(Messages.audio_not_playing)
        else:
             await ctx.send(Messages.audio_not_playing)
    
    # /resume
    @commands.command(aliases=alias.resume)
    @commands.guild_only()
    async def resume(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.is_paused():
                audio_start_time[self.bot.bot_name][ctx.guild.id] = time.perf_counter()
                await ctx.send(Messages.audio_resume)
                pause_method[self.bot.bot_name][ctx.guild.id] = 'resumeviable'
                voice_client.resume()
            elif voice_client.is_playing():
                if not ctx.guild.id in pause_method:
                   pause_method[self.bot.bot_name][ctx.guild.id] = 'None'
                
                if pause_method[self.bot.bot_name][ctx.guild.id] == 'resumeviable':
                    audio_erapsed_time[self.bot.bot_name][ctx.guild.id] += time.perf_counter() - audio_start_time[self.bot.bot_name][ctx.guild.id]
                    await ctx.send(Messages.audio_pause + ' ' + Messages.audio_erapsed_time.format(int(audio_erapsed_time[self.bot.bot_name][ctx.guild.id]) // 60, int(audio_erapsed_time[self.bot.bot_name][ctx.guild.id]) % 60))
                    pause_method[self.bot.bot_name][ctx.guild.id] = 'resume'
                    voice_client.pause()
                else:
                    await ctx.send(Messages.audio_playing.format(get_prefix(self.bot, ctx)))
            else:
                await ctx.send(Messages.audio_not_paused + '\n' + Messages.suggest_replay.format(get_prefix(self.bot, ctx)))
        else:
             await ctx.send(Messages.audio_not_paused)
    
    # /stop
    @commands.command(aliases=alias.stop)
    @commands.guild_only()
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            audio_erapsed_time[self.bot.bot_name][ctx.guild.id] += time.perf_counter() - audio_start_time[self.bot.bot_name][ctx.guild.id]
            await ctx.send(Messages.audio_stop + ' ' + Messages.audio_erapsed_time.format(int(audio_erapsed_time[self.bot.bot_name][ctx.guild.id]) // 60, int(audio_erapsed_time[self.bot.bot_name][ctx.guild.id]) % 60))
            pause_method[self.bot.bot_name][ctx.guild.id] = 'stop'
            voice_client.pause()
        elif voice_client and voice_client.is_paused():
            if not ctx.guild.id in pause_method:
                   pause_method[self.bot.bot_name][ctx.guild.id] = 'None'
            
            if pause_method[self.bot.bot_name][ctx.guild.id] == 'stop':
                await ctx.send(Messages.audio_stop_finalize)
                voice_client.stop()
            else:
                pause_method[self.bot.bot_name][ctx.guild.id] = 'stop'
                await ctx.send(Messages.audio_stop)
        else:
            await ctx.send(Messages.audio_not_playing)
    
    # /search <検索ワード>
    @commands.command(aliases=alias.search)
    @commands.guild_only()
    async def search(self, ctx, *args):
        if not args:
            await ctx.send(Messages.search_missing_argument.format(get_prefix(self.bot, ctx)))
            return
        
        fileList = self.search_audio_in_drive(args)
        await ctx.send(Messages.file_count.format(len(fileList)))
        
        if len(fileList) >= 1:
            embed = self.embed_audio_list(args, fileList, ctx.author)
            m = await ctx.send(embed = embed)
            if len(fileList) > 10:
                await m.add_reaction('◀️')
                await m.add_reaction('▶️')
            await asyncio.sleep(30)
            await m.clear_reactions()
            await m.edit(content=Messages.timeout, embed=None)
    
    # /volume <音量>
    @commands.command(aliases=alias.volume)
    @commands.guild_only()
    async def volume(self, ctx, input_volume: float):
        voice_client = ctx.guild.voice_client
        if voice_client is None or voice_client.source is None:
            await ctx.send(Messages.audio_not_playing)
            return

        if input_volume > 1.0:
            raise commands.BadArgument()
        
        voice_client.source.volume = input_volume
        await ctx.send(Messages.volume_set.format(input_volume))
    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.BadArgument):
            await ctx.send(Messages.volume_bad_argument)
        else:
            raise
    
    # リアクション(絵文字)がメッセージにつけられたときに呼び出される関数
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Botによるリアクションなら無視
        if user.bot:
            return
        
        message = reaction.message
        emoji = reaction.emoji
        
        # メッセージが自分自身のものでなければスルー
        # Embedメッセージでなければスルー
        if message.author != self.bot.user or not reaction.message.embeds:
            return
        
        embed = message.embeds[0]

        # EmbedのタイトルがSearch: でなければスルー
        # リアクションが ◀️, ▶️ でなければスルー
        if not embed.title or not embed.title.startswith('Search: ') or not emoji in {'◀️', '▶️'}:
            return
        
        # まずそのユーザーによるリアクションを削除
        await reaction.remove(user)
        # タイトルから検索ワードを抽出し、再検索
        fileList = self.search_audio_in_drive(embed.title[len('Search: '):].split(', '))
        # Embedメッセージから現在のページ数を抽出
        now_page = int(re.search(r'[0-9]+', embed.footer.text).group())
        # ファイルの数から最大ページ数を計算
        full_pages = len(fileList) // 10
        if len(fileList) % 10:
            full_pages += 1
        # 現在のページ数を更新
        dlt = 0
        if emoji == '◀️':
            dlt = -1
        else:
            dlt = 1
        if not 1 <= now_page + dlt <= full_pages:
            return
        now_page += dlt
        # ファイルの一覧を更新
        desc = ''
        count = 0
        for f in fileList[(now_page - 1) * 10:]:
            count += 1
            desc += '`{}.` {}\n\n'.format((now_page - 1) * 10 + count, f['title'])
            if count >= 10:
                break
        # 元のメッセージに 番号を入力してください が書かれていたらこっちにも付け加える
        if Messages.choice_number in embed.description:
            desc += Messages.choice_number
        # Embedメッセージを更新
        new_embed = discord.Embed(title=embed.title,description=desc)
        new_embed.set_author(name=embed.author.name,url=embed.author.url,icon_url=embed.author.icon_url)
        new_embed.set_footer(text='page {}/{}'.format(now_page, full_pages))
        await message.edit(embed=new_embed)

def setup(bot):
    bot.add_cog(audio_manager(bot))