from discord.ext import commands
from config import joined_text_channels

class VCConnection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Voice Channel Commands
    @commands.hybrid_command(name="connect", description="ボイスチャンネルに参加")
    async def connect(self, ctx):
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

    @commands.hybrid_command(name="disconnect", description="ボイスチャンネルから退出")
    async def disconnect(self, ctx):
        """ボイスチャンネルから退出"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            joined_text_channels.pop(ctx.guild.id, None)
            await ctx.send("ボイスチャンネルから退出しました。")
        else:
            await ctx.send("ボイスチャンネルに参加していません。")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot = self.bot
        # Bot自身が切断された場合
        if bot.user and member.id == bot.user.id:
            # ボイスチャンネルから退出した場合
            if before.channel is not None and after.channel is None:
                joined_text_channels.pop(member.guild.id, None)
            # チャンネル移動の場合
            elif before.channel != after.channel and after.channel is not None:
                joined_text_channels[member.guild.id] = after.channel.id

async def setup(bot):
    await bot.add_cog(VCConnection(bot))