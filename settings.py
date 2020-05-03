import json
import os
import pathlib

""" 各Botに割り振るTokenを指定
    上から順番にbot_nameがbot1, bot2, bot3...と割り振られる
"""
try:
    token = [
    os.environ['DISCORD_BOT1_TOKEN'],
    os.environ['DISCORD_BOT2_TOKEN'],
    os.environ['DISCORD_BOT3_TOKEN']
    ]
except KeyError:
    with open('./discord_token.json') as f:
        key = json.load(f)
    token = list(key.values())

# bot達のかりそめの名前
bot_name = ['bot{}'.format(i + 1) for i in range(len(token))]

# 一部コマンドの実行の際に, 開発者かどうかチェックするため, ここにアカウントIDを保管している
# 適宜変更してね
# 邦文速記研究会: 695631452980904066
DEVELOPERS_ID = [695631452980904066, 538704691777896478, 293054784288849920, 277672510823071744]
# cogs直下の.pyファイルを格納するリスト
EXTENSIONS = [path.parent.name + '.' + path.stem for path in pathlib.Path('./cogs').glob('*.py')]

# 音声ファイルの拡張子。拡張子をつける必要はないが、何のファイルか一目でわかるようにつけている
# ちなみにファイル名全体は {サーバーのID}-{bot_name}.audio となる
# プログラム正常終了時に音声ファイルは全て削除される
audio_suffix_name = '.audio'
audio_suffix = {name: '-{}'.format(name) + audio_suffix_name for name in bot_name}
# ログファイルの名前。 discord-{bot_name}.log となる
logfile = {name: 'discord-{}.log'.format(name) for name in bot_name}

""" 各Botデフォルトのプレフィックス(※コマンドの開始記号)の指定
    ここで指定しなかったBotは / に設定される
    設定例:
        default_prefix = {bot_name[1]: '!', bot_name[5]: '$'}
    注意点:
        bot_nameはTokenで指定した順番に, bot_name[0], bot_name[1], bot_name[2]...となる
        0から始まることに注意
"""
try:
    default_prefix = {bot_name[1]: '!', bot_name[2]: '$'}
except IndexError:
    # 存在しないbot_nameに対してプレフィックスを設定したときに、空っぽで初期化します
    default_prefix = {}

for bot in bot_name:
    if not bot in default_prefix:
        default_prefix[bot] = '/'

# /set_prefixにて設定された各サーバーでのプレフィックスがこの変数に保存される
guild_prefix = {name: {} for name in bot_name}
# 各Botのプレフィックスを提示する関数
# commands.Botに代入する用
def check_prefix(bot, message):
    guild = message.guild
    if guild:
        return guild_prefix[bot.bot_name].get(guild.id, default_prefix[bot.bot_name])
    else:
        return default_prefix[bot.bot_name]
# 各箇所で使用する用
def get_prefix(bot, ctx):
    guild = ctx.guild
    if guild:
        return guild_prefix[bot.bot_name].get(guild.id, default_prefix[bot.bot_name])[0]
    else:
        return default_prefix[bot.bot_name]

# 音声ファイルの再生時間を計算するために使う変数
audio_start_time = {name: {} for name in bot_name}
audio_erapsed_time = {name: {} for name in bot_name}
# /pause, /resume, /stopが使われたときにその旨を保管する変数
pause_method = {name: {} for name in bot_name}
# /randomplayを使ったときに、その時点でのドライブのファイルリストを保管する変数
# 次に/randomplayを変数なしで使ったときに参照されるので、検索ワードを入力しなくても以前と同じ条件で取得できるように。
randomfile = {name: {} for name in bot_name}

# エイリアス一覧
class alias:
    # cogs.audio_manager
    play = ['p']
    replay = ['rp']
    randomplay = ['rndp']
    seek = ['sk']
    pause = []
    resume = ['re', 'res', 'continue']
    stop = []
    search = ['s', 'find']
    volume = ['vol']
    # cogs.help_command
    help = []
    alias = []
    # cogs.manage_bot
    check_prefix = []
    set_prefix = []
    reload = []
    close = []
    # cogs.others
    neko = []
    guild_name = []
    changelog = []
    log = []
    delete = []
    # cogs.voice_client
    connect = ['c', 'join', 'summon']
    disconnect = ['dc', 'leave', 'dis']
    # cogs.yojirei
    yojirei = ['y']

# 各メッセージ一覧
class Messages:
    audio_erapsed_time = '**[{}:{:02}]**'
    audio_not_paused = ':x:**停止中の朗読はありません**'
    audio_not_playing = ':x:**朗読中ではありません**'
    audio_pause = '朗読を一時停止'
    audio_play = '再生開始'
    audio_playing = ':x:**既に朗読を再生中です\n朗読を停止するには{}pause、終了するには{}stopを使用します**'
    audio_play_before = '{}を再生準備します'
    audio_play_seek = '{}:{:02}から再生開始'
    audio_resume = '朗読再開'
    audio_stop = '朗読終了'
    audio_stop_finalize = '朗読を完全に終了します'
    changelog_bad_argument = ':x:**[表示上限数]は all もしくは 整数値 のみ許容されます**'
    check_guild_only = ':warning:このコマンドはサーバーでのみ使用できます'
    check_missing_permission = ':x:あなたに権限がありません'
    check_not_developer = ':x:このコマンドは開発者のみが使用できます'
    choice_number = '**番号を入力してください**'
    choosed_audio = '{}が選択されました'
    delete_bad_argument = ':x:**<削除件数>は整数値である必要があります**'
    delete_cancel = 'キャンセルされました'
    delete_confirm = ':warning:**直近のメッセージを{}件削除します\nよろしいですか？ y/n**'
    delete_missing_argument = ':x:**{}delete <削除件数>**'
    download_started = 'ファイルダウンロード開始'
    download_finished = 'ファイルダウンロード終了'
    file_count = '該当ファイルは{}個です'
    file_not_found = ':x:**ファイル名を検索し直してください**'
    guild_name = 'ここは {}'
    invalid_value = ':x:**値が不正です**'
    log_send = 'ログファイルを送信します'
    neko = 'にゃーん'
    play_missing_argument = ':x:**{}play <検索ワード>**'
    prefix_delete = 'サーバープレフィックスをリセットしました'
    prefix_not_found = ':x:**サーバープレフィックスが未登録です**'
    prefix_set = 'サーバープレフィックスを登録しました'
    prefix_show = 'サーバープレフィックスは {} です'
    random_nofile = ':x:**前回の検索データがありません\n{}randomplay <検索ワード>を使用してください**'
    reload = 'コグファイルを再読み込みしました'
    replay = 'もう一度再生します'
    replay_nofile = ':x:**音声ファイルが存在しません\n一度{}playや{}seekを実行してください**'
    search_missing_argument = ':x:**{}search <検索ワード>**'
    seek_bad_argument = ':x:**<開始秒数>は 90 か 1:30 のように指定してください**'
    seek_missing_argument = ':x:**{}seek <開始秒数> [検索ワード]**'
    seek_not_playing = ':x:**{}seek <開始秒数>は、再生中のみ使用できます\n{}seek <開始秒数> <検索ワード>を使用してください**'
    seek_start = '{}:{:02}地点に移動しました'
    suggest_replay = '最後に再生した朗読をもう一度再生するには{}replayコマンドを使用します'
    suggest_resume = '中断した朗読を再開する際は{}resumeコマンドを使用します'
    suggest_resume_and_stop = '停止した朗読を再開するには{}resume、終了するには{}stopを使用します'
    timeout = ':x:**タイムアウトしました**'
    voicechannel_already_connected = ':x:**既に接続しています**'
    voicechannel_connected = '接続しました'
    voicechannel_disconnected = '切断しました'
    voicechannel_not_connect = ':warning:ボイスチャンネルに接続してから実行してください'
    voicechannel_not_connect_bot = ':x:**接続していません**'
    volume_bad_argument = ':x:**音量は0.0~1.0の範囲で指定してください**'
    volume_set = '音量を{}に設定しました'
    yojirei_missing_argument = ':x:**{}yojirei <検索ワード>**'
    yojirei_not_found = 'その用字例は未登録です'
    yojirei_show = '**{}**:\n{}'
