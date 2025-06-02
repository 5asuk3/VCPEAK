import tempfile
import collections
import os
import json
import asyncio
import discord
from discord.ext import commands
from synthesize_voicepeak import synthesize_voicepeak

# トークンを外部ファイルから読み込む
with open('config.json', 'r', encoding='utf-8') as f:
    config=json.load(f)

TOKEN= config['discord_token']  # config.jsonからトークンを取得
SOUND_FILE = config['sound_file']  # 再生したい音声ファイルのパス
VOICEPEAK_PATH=config['voicepeak_path']  # Voicepeakの実行ファイルのパス

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
voice_queue = collections.defaultdict(asyncio.Queue)
playing_flags = collections.defaultdict(lambda: False)  # 再生中フラグ

@bot.command()
async def join(ctx):
    """ボイスチャンネルに参加"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
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
                text,
                tmp_path,
                VOICEPEAK_PATH
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
    
    # ボイスチャンネルに接続している場合のみ読み上げ
    voice_client = message.guild.voice_client
    if voice_client:
        await voice_queue[message.guild.id].put(message.content)
        if not playing_flags[message.guild.id]:
            await play_next(message.guild)

    await bot.process_commands(message)  # コマンドも引き続き使えるように

@bot.command()
async def leave(ctx):
    """ボイスチャンネルから退出"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("ボイスチャンネルに参加していません。")

bot.run(TOKEN)