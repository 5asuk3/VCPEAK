import tempfile
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

@bot.command()
async def join(ctx):
    """ボイスチャンネルに参加"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("ボイスチャンネルに参加しました。")
    else:
        await ctx.send("先にボイスチャンネルに参加してください。")

@bot.command()
async def play(ctx):
    """音声を再生"""
    if ctx.voice_client is None:
        await ctx.send("先に`!join`でボイスチャンネルに参加してください。")
        return
    if not ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
             tmp_path=tmp.name
        await asyncio.to_thread(
            synthesize_voicepeak,
            "こんにちは、ディスコード！",
            "output.wav",
            VOICEPEAK_PATH
        )
        source = discord.FFmpegPCMAudio("output.wav")

        def after_play(e):
            try:
                os.remove(tmp_path)
            except Exception as ex:
                print(f"一時ファイル削除エラー: {ex}")
            if e:
                print(f"再生時エラー: {e}")

        ctx.voice_client.play(source, after=after_play)
        await ctx.send("音声を再生します。")
    else:
        await ctx.send("すでに再生中です。")

@bot.command()
async def leave(ctx):
    """ボイスチャンネルから退出"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("ボイスチャンネルに参加していません。")

bot.run(TOKEN)