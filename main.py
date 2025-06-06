import os
import sys
import discord
from discord import app_commands
from discord.ext import commands
from config import TOKEN, PREFIX, SERVER_DEFAULT, NARRATORS, EMOTIONS, EMBED_DEFAULT, server_settings, joined_text_channels
from json_loader import save_json
from message_parser import parse_message, pre_parse_message
from vp_service import vp_play

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

async def setup_hook():
    await bot.load_extension("cogs.dictionary")  # 辞書関連のコグを読み込み
    await bot.load_extension("cogs.user_config")  # ユーザー設定関連のコグを読み込み
    await bot.load_extension("cogs.server_config")  # サーバー設定関連のコグを読み込み
    await bot.load_extension("cogs.admin_commands")  # 管理者コマンド関連のコグを読み込み

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    await bot.tree.sync()
    EMBED_DEFAULT.set_author(name=bot.user.name, url="https://github.com/5asuk3/VCPEAK", icon_url=bot.user.avatar.url)
    print(f"Logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    print(f"Botがサーバー「{guild.name}」({guild.id}) に参加しました。")
    if str(guild.id) not in server_settings:
        server_settings[str(guild.id)] = SERVER_DEFAULT.copy()
        save_json("servers.json", server_settings)



@bot.hybrid_command(name="voice-list", description="キャラクター一覧の表示")
async def get_narrator(ctx):
    """キャラクター一覧の表示"""
    embed= EMBED_DEFAULT.copy()
    embed.title = "キャラクター一覧"
    embed.description = "現在使用可能なキャラクターと感情の一覧です。\n感情はキャラクターごとに内容が異なります。"
    for narrator in NARRATORS:
        emotion=", ".join(EMOTIONS[narrator])
        embed.add_field(name=narrator, value=f"感情一覧:{emotion}", inline=False)
    await ctx.send(embed=embed)

# Voice Channel Commands
@bot.hybrid_command(name="connect", description="ボイスチャンネルに参加")
async def connect(ctx):
    """ボイスチャンネルに参加"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # すでにボイスチャンネルに参加している場合
        if ctx.guild.voice_client is not None:
            await ctx.send("すでにボイスチャンネルに参加しています。")
            return
        await channel.connect()
        joined_text_channels[ctx.guild.id] = ctx.channel.id
        await ctx.send("ボイスチャンネルに参加しました。")
    else:
        await ctx.send("先にボイスチャンネルに参加してください。")

@bot.hybrid_command(name="disconnect", description="ボイスチャンネルから退出")
async def disconnect(ctx):
    """ボイスチャンネルから退出"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        joined_text_channels.pop(ctx.guild.id, None)
        await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("ボイスチャンネルに参加していません。")

@bot.event
async def on_voice_state_update(member, before, after):
    # Bot自身が切断された場合
    if member.id == bot.user.id:
        # ボイスチャンネルから退出した場合
        if before.channel is not None and after.channel is None:
            joined_text_channels.pop(member.guild.id, None)
        # チャンネル移動の場合
        elif before.channel != after.channel and after.channel is not None:
            joined_text_channels[member.guild.id] = after.channel.id

# TTS Event
@bot.event
async def on_message(message):
    # コマンドは読み上げない
    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.process_commands(message)
        return
    
    # Bot自身のメッセージは無視
    if (message.author.bot 
        or message.guild.id not in joined_text_channels
        or message.channel.id != joined_text_channels[message.guild.id]
    ):
        return
    
    # ボイスチャンネルに接続している場合のみ読み上げ
    voice_client = message.guild.voice_client
    if voice_client:
        text = []
        # 本文があれば追加
        if message.content.strip():
            text.append(pre_parse_message(message))
        # スタンプがあれば追加
        if message.stickers:
            text.append(f"{message.stickers[0].name}のスタンプ")
        # 添付ファイルがあれば追加
        if message.attachments:
            text.append(f"添付ファイルが送信されました")
        # スタンプと本文を結合・整形
        raw_message = "、".join(text)

        parsed_message=parse_message(raw_message)
        await vp_play(bot, parsed_message, message.guild, message.author)

# Utility Commands
bot.remove_command("help")  # デフォルトのヘルプコマンドを削除
@bot.hybrid_command(name="help", description="ヘルプメッセージを表示")
async def help_command(ctx):
    embed = EMBED_DEFAULT.copy()
    embed.title = "VCPEAK ヘルプ"
    embed.add_field(name="/connect", value="ボイスチャンネルへの参加", inline=False)
    embed.add_field(name="/disconnect", value="ボイスチャンネルからの退出", inline=False)
    embed.add_field(name="/voice-list", value="キャラクター一覧の取得", inline=False)
    embed.add_field(name="/dict", value="ことばリスト関連のコマンド", inline=False)
    embed.add_field(name="/config", value="ユーザー設定関連のコマンド", inline=False)
    embed.add_field(name="/server-config", value="サーバー設定関連のコマンド", inline=False)
    embed.add_field(name="/restart", value="ボットの再起動(要注意！)", inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)