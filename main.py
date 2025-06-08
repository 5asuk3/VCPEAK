import discord
from discord.ext import commands
from config import TOKEN, PREFIX

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.hybrid_command(name="ping", description="Botの応答速度を確認")
async def ping(ctx):
    """Botの応答速度を確認"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="Ping", description=f"現在の応答速度: {latency}ms", color=discord.Color.blue())
    await ctx.send(embed=embed)

async def setup_hook():
    await bot.load_extension("cogs.dictionary")  # 辞書関連のコグを読み込み
    await bot.load_extension("cogs.user_config")  # ユーザー設定関連のコグを読み込み
    await bot.load_extension("cogs.server_config")  # サーバー設定関連のコグを読み込み
    await bot.load_extension("cogs.vc_connection")  # ボイスチャンネル接続関連のコグを読み込み
    await bot.load_extension("cogs.tts")  # TTS関連のコグを読み込み
    await bot.load_extension("cogs.utility_commands")  # ユーティリティコマンド関連のコグを読み込み


bot.setup_hook = setup_hook
bot.run(TOKEN)