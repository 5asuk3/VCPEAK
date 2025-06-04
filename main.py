import os
import sys
import discord
from discord.ext import commands
from vp_service import vp_play
from json_loader import *
from config import *
from message_parser import parse_message

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

joined_text_channels={}
embed_default = discord.Embed(
    title="VCPeak",
    description="aaaaa",
    color=discord.Color.blue()
)
embed_default.set_footer(text="VCPeak Bot")

@bot.event
async def on_ready():
    await bot.tree.sync()
    if bot.user.avatar:
        embed_default.set_thumbnail(url=bot.user.avatar.url)
        
    print(f"Logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    print(f"Botがサーバー「{guild.name}」({guild.id}) に参加しました。")
    if str(guild.id) not in server_settings:
        server_settings[str(guild.id)] = server_default.copy()
        save_json("servers.json", server_settings)



# Config Commands
@bot.hybrid_group(name="server-config", description="設定関連のコマンド")
async def server_config(ctx):
    server_id = str(ctx.guild.id)
    if server_id not in server_settings:
        server_settings[server_id] = server_default.copy()

    if ctx.invoked_subcommand is None:
        await ctx.send("設定コマンドを実行するには、サブコマンドを指定してください。")

@server_config.command(name="show", description="サーバー設定を表示")
async def show_server_config(ctx):
    """サーバー設定を表示"""
    server_id = str(ctx.guild.id)
    settings = server_settings[server_id]
    embed = discord.Embed(title=f"{ctx.guild.name}の設定", color=discord.Color.blue())
    for key, value in settings.items():
        embed.add_field(name=key, value=str(value), inline=False)
    
    await ctx.send(embed=embed) 

@server_config.command(name="volume", description="ボイスチャンネルの音量を設定")
async def set_volume(ctx, volume: int=100):
    """ボイスチャンネルの音量を設定"""
    if volume < 0 or volume > 200:
        await ctx.send("音量は0から200の範囲で設定してください。")
        return
    
    server_settings[str(ctx.guild.id)]["volume"] = volume
    save_json("servers.json", server_settings)
    
    await ctx.send(f"ボイスチャンネルの音量を{volume}%に設定しました。")

@bot.hybrid_group(name="config", description="ユーザー設定")
async def user_config(ctx):
    user_id = str(ctx.author.id)
    if str(user_id) not in user_settings:
        user_settings[user_id] = user_default.copy()
        save_json("users.json", user_settings)

    if ctx.invoked_subcommand is None:
        await ctx.send("ユーザー設定コマンドを実行するには、サブコマンドを指定してください。")

@user_config.command(name="show", description="ユーザー設定を表示")
async def show_user_config(ctx):
    """ユーザー設定を表示"""
    settings = user_settings[str(ctx.author.id)]
    embed = discord.Embed(title=f"{ctx.author.name}の設定", color=discord.Color.blue())
    for key, value in settings.items():
        embed.add_field(name=key, value=str(value), inline=False)
    
    await ctx.send(embed=embed)
    
@user_config.command(name="narrator", description="キャラクターを設定")
async def set_narrator(ctx, narrator: str=""):
    """キャラクターを設定"""
    if narrator not in narrators:
        await ctx.send(f"引数がない、もしくは無効なキャラクターです。\n利用可能なキャラクター: {', '.join(narrators)}")
        return
    user_id = str(ctx.author.id)
    user_settings[user_id]["narrator"] = narrator
    value=", ".join(f"{emotion}=0" for emotion in emotions[narrator])
    user_settings[user_id]["emotion"]=value
    save_json("users.json", user_settings)
    await ctx.send(f"キャラクターを「{narrator}」に設定しました。")

@user_config.command(name="emotion", description="感情を設定")
async def set_emotion(ctx, emotion: str=""):
    """感情を設定"""
    await ctx.send("まだ未対応だよ～ん")

@user_config.command(name="speed", description="音声の速度を設定")
async def set_speed(ctx, speed: int=100):
    if speed < 50 or speed > 200:
        await ctx.send("速度は50から200の範囲で設定してください。")
        return
    
    user_settings[str(ctx.author.id)]["speed"] = speed
    save_json("users.json", user_settings)
    await ctx.send(f"音声の速度を{speed}%に設定しました。")

@user_config.command(name="pitch", description="音声のピッチを設定")
async def set_pitch(ctx, pitch: int=100):
    if pitch < -300 or pitch > 300:
        await ctx.send("ピッチは-300から300の範囲で設定してください。")
        return
    
    user_settings[str(ctx.author.id)]["pitch"] = pitch
    save_json("users.json", user_settings)
    await ctx.send(f"音声のピッチを{pitch}%に設定しました。")


@bot.hybrid_command(name="voice-list", description="キャラクター一覧の表示")
async def get_narrator(ctx):
    """キャラクター一覧の表示"""
    embed = discord.Embed(title="キャラクター一覧", color=discord.Color.green())
    for narrator in narrators:
        emotion=", ".join(emotions[narrator])
        embed.add_field(name=narrator, value=emotion, inline=False)
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
        parsed_message=parse_message(message.content)
        await vp_play(bot, parsed_message, message.guild, message.author)

# Utility Commands
bot.remove_command("help")  # デフォルトのヘルプコマンドを削除
@bot.hybrid_command(name="help", description="ヘルプメッセージを表示")
async def help_command(ctx):
    embed = discord.Embed(title="VCPEAK Bot ヘルプ", color=discord.Color.blue())
    embed.add_field(name="/connect", value="ボイスチャンネルへの参加", inline=False)
    embed.add_field(name="/disconnect", value="ボイスチャンネルからの退出", inline=False)
    embed.add_field(name="/get-voice", value="話者一覧の取得", inline=False)
    embed.add_field(name="/config", value="ユーザー設定関連のコマンド", inline=False)
    embed.add_field(name="/server-config", value="サーバー設定関連のコマンド", inline=False)
    embed.add_field(name="/restart", value="ボットの再起動(要注意！)", inline=False)
    embed.set_footer(text="https://github.com/5asuk3/VCPEAK-Bot")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="restart", description="ボットを再起動")
async def restart(ctx):
    for guild_id, channel_id in joined_text_channels.items():
        guild = bot.get_guild(guild_id)
        channel=guild.get_channel(channel_id)
        if channel is not None:
            try:
                await channel.send("ボットを再起動します。\n再起動後、必要に応じて/joinコマンドを使用して再接続させてください。")
            except Exception as e:
                print(f"メッセージ送信エラー: {e}") 
    await bot.close()  # Discordとの接続を閉じる
    os.execv(sys.executable, [sys.executable] + sys.argv)  # プロセスを再起動

@bot.hybrid_command(name="embedtest", description="Embedメッセージのテスト")
async def embedtest(ctx):
    embed=embed_default.copy()
    embed.add_field(name="フィールド1", value="値1", inline=False)
    embed.add_field(name="フィールド2", value="値2", inline=True)
    await ctx.send(embed=embed)

bot.run(TOKEN)