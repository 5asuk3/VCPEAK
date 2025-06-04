
import os
import json
import asyncio
import discord
from discord.ext import commands    
from vp_service import *
from json_loader import *
import subprocess

try:
    result = subprocess.run([VOICEPEAK_PATH, "--list-narrator"], check=True, stdout=subprocess.PIPE, text=True)
    narrators=result.stdout.strip().splitlines()
except subprocess.CalledProcessError as e:
    print(f"話者取得に失敗しました: {e}")
    raise

print(narrators)
print(server_settings)
print(user_settings)

base_embed = discord.Embed(
    title="VCPeak",
    description="aaaaa",
    color=discord.Color.blue()
)
base_embed.set_footer(text="VCPeak Bot")


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    print(f"Botがサーバー「{guild.name}」({guild.id}) に参加しました。")
    if str(guild.id) not in server_settings:
        server_settings[str(guild.id)] = server_default.copy()
        save_json("servers.json", server_settings)
    

@bot.hybrid_group(name="config", description="設定関連のコマンド")
async def config(ctx):
    """設定関連のコマンド"""
    if ctx.invoked_subcommand is None:
        await ctx.send("設定コマンドを実行するには、サブコマンドを指定してください。")
    # if user_id not in user_settings:
    #     user_settings[user_id] = user_default.copy()
    #     save_json("users.json", user_settings)

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
        await vp_play(bot, message.content, message.guild, message.author)

@bot.hybrid_command(name="leave", description="ボイスチャンネルから退出")
async def leave(ctx):
    """ボイスチャンネルから退出"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("ボイスチャンネルに参加していません。")

@bot.hybrid_command(name="embedtest", description="Embedメッセージのテスト")
async def embedtest(ctx):
    embed=base_embed.copy()
    embed.add_field(name="フィールド1", value="値1", inline=False)
    embed.add_field(name="フィールド2", value="値2", inline=True)
    embed.set_thumbnail(url="https://example.com/image.png")
    await ctx.send(embed=embed)

bot.run(TOKEN)