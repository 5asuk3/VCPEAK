import tempfile
import collections
import os
import json
import asyncio
import discord
from discord.ext import commands    
from vp_service import synthesize_voicepeak
import subprocess

# トークンを外部ファイルから読み込む
with open('config.json', 'r', encoding='utf-8') as f:
    data=json.load(f)

with open('servers.json', 'r', encoding='utf-8') as f:
    server_settings=json.load(f)

config=data['config']
user_default=data['user_default']
server_default=data['server_default']

TOKEN= config['discord_token']  # config.jsonからトークンを取得
VOICEPEAK_PATH=config['voicepeak_path']  # Voicepeakの実行ファイルのパス

try:
    result = subprocess.run([VOICEPEAK_PATH, "--list-narrator"], check=True, stdout=subprocess.PIPE, text=True)
    narrators=result.stdout.strip().splitlines()
except subprocess.CalledProcessError as e:
    print(f"話者取得に失敗しました: {e}")
    raise

print(narrators)


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
voice_queue = collections.defaultdict(asyncio.Queue)
playing_flags = collections.defaultdict(lambda: False)  # 再生中フラグ

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    print(f"Botがサーバー「{guild.name}」({guild.id}) に参加しました。")
    if guild.id not in server_settings:
        server_settings[guild.id] = server_default.copy()
        with open('servers.json', 'w', encoding='utf-8') as f:
            json.dump(server_settings, f, indent=4)
    

@bot.hybrid_group(name="config", description="設定関連のコマンド")
async def config(ctx):
    """設定関連のコマンド"""
    if ctx.invoked_subcommand is None:
        await ctx.send("設定コマンドを実行するには、サブコマンドを指定してください。")

# @config.command(name="narrator", description="ナレーターを設定")
# @config.command(name="emotion", description="感情を設定")

@bot.hybrid_command(name="join", description="ボイスチャンネルに参加")
async def join(ctx):
    """ボイスチャンネルに参加"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # すでにボイスチャンネルに参加している場合
        if ctx.guild.voice_client is not None:
            await ctx.send("すでにボイスチャンネルに参加しています。")
            return
        await channel.connect()
        await ctx.send("ボイスチャンネルに参加しました。")
    else:
        await ctx.send("先にボイスチャンネルに参加してください。")


async def play_next(guild):
    if playing_flags[guild.id]:
        return
    playing_flags[guild.id]=True
    try:
        voice_client=guild.voice_client
        if not voice_client:
            return
        
        queue=voice_queue[guild.id]
        while not queue.empty():
            
            text=await queue.get()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path=tmp.name
            await asyncio.to_thread(
                synthesize_voicepeak,
                VOICEPEAK_PATH,
                tmp_path,
                text,
                "",
                ""
            )
            source = discord.FFmpegPCMAudio(tmp_path)

            play_finished=asyncio.Event()

            def after_play(e):
                try:
                    os.remove(tmp_path)
                except Exception as ex:
                    print(f"一時ファイル削除エラー: {ex}")
                if e:
                    print(f"再生時エラー: {e}")
                        # 次の音声を再生
                bot.loop.call_soon_threadsafe(play_finished.set)

                
            voice_client.play(source, after=after_play)
            await play_finished.wait()
    finally:
        playing_flags[guild.id]=False


@bot.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author.bot:
        return

    # コマンドは読み上げない
    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.process_commands(message)
        return
    
    # ボイスチャンネルに接続している場合のみ読み上げ
    voice_client = message.guild.voice_client
    if voice_client:
        await voice_queue[message.guild.id].put(message.content)
        if not playing_flags[message.guild.id]:
            await play_next(message.guild)

@bot.hybrid_command(name="leave", description="ボイスチャンネルから退出")
async def leave(ctx):
    """ボイスチャンネルから退出"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("ボイスチャンネルに参加していません。")

@bot.hybrid_command(name="test", description="Hybrid command example")
async def test(ctx):
    await ctx.send("This is a hybrid command!")

bot.run(TOKEN)