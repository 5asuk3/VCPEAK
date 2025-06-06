import os
import sys
from discord.ext import commands
from config import EMBED_DEFAULT, joined_text_channels
class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="restart", description="ボットを再起動")
    async def restart(self, ctx):
        """ボットを再起動"""
        embed= EMBED_DEFAULT.copy()
        embed.title = "ボットを再起動します。"
        embed.description = "再起動後、必要に応じて/connectコマンドを使用して再接続させてください。"
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