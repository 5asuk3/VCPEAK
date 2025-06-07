from discord.ext import commands
from config import joined_text_channels
from vp_service import vp_play

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
                if ctx.guild.voice_client.channel != channel:
                    await ctx.guild.voice_client.move_to(channel)
                    joined_text_channels[ctx.guild.id] = ctx.channel.id
                    await ctx.send("ボイスチャンネルを移動しました。")
                    return
                else:
                    await ctx.voice_client.disconnect()
                    await channel.connect()
                    joined_text_channels[ctx.guild.id] = ctx.channel.id
                    await ctx.send("すでにボイスチャンネルに参加しているため、再参加します。")
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
        voice_client = member.guild.voice_client
        if not (before.channel == voice_client.channel or after.channel == voice_client.channel):
            return
        if after.channel != before.channel and member.id != bot.user.id:
            text_channel=bot.get_channel(joined_text_channels.get(member.guild.id))
            if before.channel is None and after.channel is not None:
                await text_channel.send(f"{member.display_name}({member.name})がボイスチャンネルに参加しました。")
            elif before.channel is not None and after.channel is None:
                await text_channel.send(f"{member.display_name}({member.name})がボイスチャンネルから退出しました。")
            elif before.channel is not None and after.channel is not None:
                if before.channel.id == voice_client.channel.id:
                    await text_channel.send(f"{member.display_name}({member.name})がボイスチャンネルを移動しました。")
                elif after.channel.id == voice_client.channel.id:
                    await text_channel.send(f"{member.display_name}({member.name})がボイスチャンネルに参加しました。")

async def setup(bot):
    await bot.add_cog(VCConnection(bot))