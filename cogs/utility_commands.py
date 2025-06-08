import os
import sys
import discord
from discord.ext import commands
from config import NARRATORS, EMOTIONS, SERVER_DEFAULT, USER_DEFAULT, EMBED_DEFAULT, EMBED_COLOR_ERROR, joined_text_channels
from utils import is_owner_or_admin, handle_check_fauilure


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")  # デフォルトのヘルプコマンドを削除


    @commands.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        await bot.tree.sync()
        print(f"Logged in as {bot.user}")
        EMBED_DEFAULT.set_author(name=bot.user.name, url="https://github.com/5asuk3/VCPEAK", icon_url=bot.user.display_avatar.url) if bot.user else None

        print("利用可能なキャラクター:")
        for narrator in NARRATORS:
            print(f"\tナレーター: {narrator}\t感情: {', '.join(EMOTIONS[narrator])}")
        print("サーバーのデフォルト設定:")
        print(f"\t", ", ".join(f"{key}={value}" for key, value in SERVER_DEFAULT.items()))
        print("ユーザーのデフォルト設定:")
        print(f"\t", ", ".join(f"{key}={value}" for key, value in USER_DEFAULT.items()))

        print("現在入っているサーバー:")
        for guild in bot.guilds:
            print(f"\tサーバー名: {guild.name}({guild.id})")


    # Utility Commands
    @commands.hybrid_command(name="voice-list", description="キャラクター一覧の表示")
    async def get_narrator(self, ctx):
        """キャラクター一覧の表示"""
        embed= EMBED_DEFAULT.copy()
        embed.title = "キャラクター一覧"
        embed.description = "現在使用可能なキャラクターと感情の一覧です。\n感情はキャラクターごとに内容が異なります。"
        for narrator in NARRATORS:
            emotion=", ".join(EMOTIONS[narrator])
            embed.add_field(name=narrator, value=f"感情一覧:{emotion}", inline=False)
        await ctx.send(embed=embed)


    @commands.hybrid_command(name="ping", description="Botの応答速度を確認")
    async def ping(self, ctx):
        """Botの応答速度を確認"""
        bot=self.bot
        latency = round(bot.latency * 1000)
        
        embed = EMBED_DEFAULT.copy()
        embed.title = "応答速度"
        embed.description = f"現在の応答速度: {latency}ms"
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="info", description="Botの情報を表示")
    async def info(self, ctx):
        """Botの情報を表示"""
        bot = self.bot
        embed = EMBED_DEFAULT.copy()
        embed.title = "VCPEAK INFO"
        embed.description = ("VCPEAKは、ボイスチャンネルでのTTS(Text To Speech)を提供するDiscord Botです。\n"
            "VOICEPEAKの最新AI音声合成技術を用いた高品質な音声でテキストを読み上げることが出来ます。\n"
            "\n"
            "`/connect`でボイスチャンネルへ参加、`/disconnect`でボイスチャンネルから切断できます。\n"
            "その他コマンドの簡易ヘルプは`/help`で確認できます。\n"
            "\n"
            "詳細は https://github.com/5asuk3/vcpeak へ。\n")
        embed.set_thumbnail(url=bot.user.display_avatar.url) if bot.user else None
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="help", description="ヘルプメッセージを表示")
    async def help_command(self, ctx):
        embed = EMBED_DEFAULT.copy()
        embed.title = "VCPEAK ヘルプ"
        embed.add_field(name="/connect", value="ボイスチャンネルへの参加", inline=False)
        embed.add_field(name="/disconnect", value="ボイスチャンネルからの退出", inline=False)
        embed.add_field(name="/voice-list", value="キャラクター一覧の取得", inline=False)
        embed.add_field(name="/dict", value="ことばリスト関連のコマンド", inline=False)
        embed.add_field(name="/config", value="ユーザー設定関連のコマンド", inline=False)
        embed.add_field(name="/server-config", value="サーバー設定関連のコマンド", inline=False)
        await ctx.send(embed=embed)
        return


    @commands.hybrid_command(name="reload", description="モジュールの再読み込み")
    async def reload(self, ctx):
        bot = self.bot
        embed = EMBED_DEFAULT.copy()
        embed.title = "モジュールの再読み込み"
        success = []
        failed = []
        for ext in list(bot.extensions):
            if ext == "cogs.utility_commands":
                continue
            try:
                await bot.reload_extension(ext)
                success.append(ext)
            except Exception as e:
                failed.append(f"{ext}（{e}）")
        desc = ""
        if success:
            desc += f"再読み込み成功: {', '.join(success)}\n"
        if failed:
            desc += f"再読み込み失敗: {', '.join(failed)}"
        if not desc:
            desc = "再読み込み対象がありませんでした。"
        embed.description = desc
        await ctx.send(embed=embed)


    @is_owner_or_admin()
    @commands.hybrid_command(name="restart", description="ボットの再起動")
    async def restart(self, ctx):
        """ボットを再起動"""
        bot = self.bot
        embed= EMBED_DEFAULT.copy()
        embed.title = "ボットの再起動"
        embed.description = "ボットを再起動します。再起動後、必要に応じて/connectコマンドを使用して再接続させてください。"
        for guild_id, channel_id in joined_text_channels.items():
            guild = bot.get_guild(guild_id)
            channel=guild.get_channel(channel_id)
            if channel is not None and guild is not ctx.guild:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"メッセージ送信エラー: {e}") 
        await ctx.send(embed=embed)
        await bot.close()  # Discordとの接続を閉じる
        os.execv(sys.executable, [sys.executable] + sys.argv)  # プロセスを再起動


    async def cog_command_error(self, ctx, error):
        embed= EMBED_DEFAULT.copy()
        embed.title = "コマンドエラー"
        embed.description = str(error)
        embed.color = EMBED_COLOR_ERROR
        if await handle_check_fauilure(ctx, error, embed):
            return
        else:
            raise error # 他のエラーは通常通り
        

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))