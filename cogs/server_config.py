from discord.ext import commands
from json_loader import save_json
from config import EMBED_DEFAULT, server_settings, SERVER_DEFAULT

class ServerConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def ensure_server_settings(self, server_id):
        if server_id not in server_settings:
            server_settings[server_id] = SERVER_DEFAULT.copy()
            save_json("servers.json", server_settings)
            
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Botがサーバー「{guild.name}」({guild.id}) に参加しました。")
        if str(guild.id) not in server_settings:
            server_settings[str(guild.id)] = SERVER_DEFAULT.copy()
            save_json("servers.json", server_settings)

    # server setting command
    @commands.hybrid_group(name="server-config", description="設定関連のコマンド")
    async def server_config(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.show_server_config(ctx)

    @server_config.command(name="list", description="サーバー設定を表示")
    async def show_server_config(self, ctx):
        """サーバー設定を表示"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.guild.name}のサーバー設定"
        embed.description = "/server-config reset でデフォルト値にリセットできます。"

        server_id = str(ctx.guild.id)
        self.ensure_server_settings(server_id)
        settings = server_settings[server_id]
        embed.add_field(name="音量", value=settings['volume'], inline=False)
        
        await ctx.send(embed=embed) 

    @server_config.command(name="volume", description="ボイスチャンネルの音量を設定")
    async def set_volume(self, ctx, volume: int=SERVER_DEFAULT['volume']):
        """ボイスチャンネルの音量を設定"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.guild.name}のサーバー設定"

        if volume < 0 or volume > 200:
            embed.description = "音量は0から200の範囲で設定してください。"
            await ctx.send(embed=embed)
            return
        
        server_id=str(ctx.guild.id)
        self.ensure_server_settings(server_id)
        server_settings[server_id]["volume"] = volume
        save_json("servers.json", server_settings)
        
        embed.description = f"ボイスチャンネルの音量を{volume}%に設定しました。"
        await ctx.send(embed=embed)


    @server_config.command(name="reset", description="サーバー設定をデフォルトにリセット")
    async def reset_server_config(self, ctx):
        """サーバー設定をデフォルトにリセット"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.guild.name}のサーバー設定"
        embed.description = "サーバー設定をデフォルト値にリセットしました。"

        server_id = str(ctx.guild.id)
        server_settings[server_id] = SERVER_DEFAULT.copy()
        save_json("servers.json", server_settings)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerConfig(bot))
