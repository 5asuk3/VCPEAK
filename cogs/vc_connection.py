import itertools
from discord.ext import commands
from config import SERVER_DEFAULT, server_settings, joined_text_channels
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
                    await ctx.send("ボイスチャンネルを移動しました。")
                    joined_text_channels[ctx.guild.id] = ctx.channel.id
                    return
                else:
                    await ctx.voice_client.disconnect()
                    await channel.connect()
                    await ctx.send("すでにボイスチャンネルに参加しているため、再参加します。")
                    joined_text_channels[ctx.guild.id] = ctx.channel.id
                    return
            await channel.connect()
            await ctx.send("ボイスチャンネルに参加しました。")
            joined_text_channels[ctx.guild.id] = ctx.channel.id
        else:
            await ctx.send("先にボイスチャンネルに参加してください。")


    @commands.hybrid_command(name="disconnect", description="ボイスチャンネルから退出")
    async def disconnect(self, ctx):
        """ボイスチャンネルから退出"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("ボイスチャンネルから退出しました。")
            joined_text_channels.pop(ctx.guild.id, None)
        else:
            await ctx.send("ボイスチャンネルに参加していません。")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot = self.bot
        voice_client = member.guild.voice_client
        text_channel=bot.get_channel(joined_text_channels.get(member.guild.id))

        if ((member.id == bot.user.id)
             or (before.channel and after.channel)
             or not ((before.channel and before.channel.id == voice_client.channel.id) or (after.channel and after.channel.id == voice_client.channel.id))
            ):
            return
        
        # TODO自動入室
        # all_members=list(itertools.chain.from_iterable(vc.members for vc in member.guild.voice_channels))
        # # 参加していないとき、設定されているサーバーに自動でボイスチャンネルに参加する
        # if (not voice_client 
        #     and server_settings[str(member.guild.id)]["auto_connect"] 
        #     and (after.channel and after.channel.guild.id == member.guild.id) 
        #     # and (not all_members or all(member.bot for member in all_members))
        #     ):
        #     await after.channel.connect()
        #     await text_channel.send(f"ボイスチャンネルに自動で参加しました。")
        #     joined_text_channels[member.guild.id] = server_settings[str(member.guild.id)]["auto_connect"]
        #     return
            
        # 参加していないボイスチャンネルについては何もしない
        if not voice_client:
            return

        # ボイスチャンネルに参加者がいない場合、設定に応じて自動で退出する
        if server_settings[str(member.guild.id)].get("auto_disconnect", SERVER_DEFAULT["auto_disconnect"]):
            if all(member.bot for member in voice_client.channel.members):
                await voice_client.disconnect()
                await text_channel.send(f"参加者がいなくなったため、ボイスチャンネルから退出しました。")
                joined_text_channels.pop(member.guild.id, None)
                return
        

        # ボイスチャンネルの参加・退出・移動を検知
        if after.channel != before.channel and member.id != bot.user.id:
            text = ""
            text_channel=bot.get_channel(joined_text_channels.get(member.guild.id))
            if before.channel is None and after.channel is not None:
                await text_channel.send(f":inbox_tray:`{member.display_name}(@{member.name})`がボイスチャンネルに参加しました。")
                text=f"{member.display_name}がボイスチャンネルに参加しました。"
            elif before.channel is not None and after.channel is None:
                await text_channel.send(f":outbox_tray:`{member.display_name}(@{member.name})`がボイスチャンネルから退出しました。")
                text=f"{member.display_name}がボイスチャンネルから退出しました。"
            elif before.channel is not None and after.channel is not None:
                if before.channel.id == voice_client.channel.id:
                    await text_channel.send(f":outbox_tray:`{member.display_name}(@{member.name})`がボイスチャンネルを移動しました。")
                    text=f"{member.display_name}がボイスチャンネルを移動しました。"
                elif after.channel.id == voice_client.channel.id:
                    await text_channel.send(f":inbox_tray:`{member.display_name}(@{member.name})`がボイスチャンネルに参加しました。")
                    text=f"{member.display_name}がボイスチャンネルに参加しました。"
            # サーバー設定に応じて読み上げ
            if server_settings[str(member.guild.id)].get('announce_join_leave', SERVER_DEFAULT['announce_join_leave']):
                await vp_play(bot, text, member.guild, bot.user)


async def setup(bot):
    await bot.add_cog(VCConnection(bot))