import os
import sys
from discord.ext import commands
from config import EMBED_DEFAULT, joined_text_channels
class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="reload", description="モジュールの再読み込み")
    async def reload(self, ctx):
        embed = EMBED_DEFAULT.copy()
        embed.title = "モジュールの再読み込み"
        success = []
        failed = []
        for ext in list(self.bot.extensions):
            if ext == "cogs.admin_commands":
                continue
            try:
                await self.bot.reload_extension(ext)
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

    @commands.has_permissions(administrator=True)
    @commands.hybrid_command(name="restart", description="ボットの再起動")
    async def restart(self, ctx):
        """ボットを再起動"""
        embed= EMBED_DEFAULT.copy()
        embed.title = "ボットの再起動"
        embed.description = "ボットを再起動します。再起動後、必要に応じて/connectコマンドを使用して再接続させてください。"
        for guild_id, channel_id in joined_text_channels.items():
            guild = self.bot.get_guild(guild_id)
            channel=guild.get_channel(channel_id)
            if channel is not None and guild is not ctx.guild:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"メッセージ送信エラー: {e}") 
        await ctx.send(embed=embed)
        await self.bot.close()  # Discordとの接続を閉じる
        os.execv(sys.executable, [sys.executable] + sys.argv)  # プロセスを再起動

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))