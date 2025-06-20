from discord.ext import commands
from config import SERVER_DEFAULT, server_settings, joined_text_channels, EMBED_DEFAULT, EMBED_COLOR_ERROR
from message_parser import parse_message
from vp_service import vp_play


class VCConnection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Voice Channel Commands
    @commands.hybrid_command(name="connect", description="ボイスチャンネルに参加")
    async def connect(self, ctx):
        """ボイスチャンネルに参加"""
        if ctx.author.voice and ctx.author.voice.channel.permissions_for(ctx.guild.me).connect:
            channel = ctx.author.voice.channel
            embed = EMBED_DEFAULT.copy()
            # すでにボイスチャンネルに参加している場合
            if ctx.guild.voice_client is not None:
                if ctx.guild.voice_client.channel != channel:
                    await ctx.guild.voice_client.move_to(channel)
                    joined_text_channels[ctx.guild.id] = ctx.channel.id
                    embed.title = ":incoming_envelope:ボイスチャンネル間の移動"
                    embed.description = "ボイスチャンネルを移動しました。"
                    await ctx.send(embed=embed)
                    return
                else:
                    await ctx.voice_client.disconnect()
                    await channel.connect()
                    await ctx.voice_client.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
                    embed.title = ":arrows_counterclockwise:ボイスチャンネルへの再参加"
                    embed.description = "すでにボイスチャンネルに参加していたため、再参加しました。"
                    await ctx.send(embed=embed)
                    joined_text_channels[ctx.guild.id] = ctx.channel.id
                    return
            await channel.connect()
            await ctx.voice_client.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            joined_text_channels[ctx.guild.id] = ctx.channel.id
            embed.title = ":speech_balloon:ボイスチャンネルへの参加"
            embed.description = "ボイスチャンネルに参加しました。"
            await ctx.send(embed=embed)
        else:
            embed.title = ":warning:参加エラー"
            embed.description = "ボイスチャンネルに参加できません。\nボイスチャンネルに参加してからコマンドを実行してください。\nすでに参加している場合は、botがそのチャンネルに参加する権限があることを確認してください。"
            embed.color = EMBED_COLOR_ERROR
            await ctx.send(embed=embed)


    @commands.hybrid_command(name="disconnect", description="ボイスチャンネルから退出")
    async def disconnect(self, ctx):
        """ボイスチャンネルから退出"""
        embed= EMBED_DEFAULT.copy()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            embed.title = ":zzz:ボイスチャンネルからの退出"
            embed.description = "ボイスチャンネルから退出しました。"
            await ctx.send(embed=embed)
            joined_text_channels.pop(ctx.guild.id, None)
        else:
            embed.title = ":warning:退出エラー"
            embed.description = "ボイスチャンネルに参加していません。"
            embed.color = EMBED_COLOR_ERROR
            await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot = self.bot
        voice_client = member.guild.voice_client

        # ボット本人もしくはチャンネル間の移動がない場合は何もしない
        if after.channel == before.channel or member.id == bot.user.id:
            return
        
        # ボイスチャンネルに参加しておらず、参加したチャンネルがありそのチャンネルの自動参加設定が有効の場合
        if (not voice_client
             and after.channel
             and server_settings[str(member.guild.id)].get("auto_connect", {})
             and server_settings[str(member.guild.id)]["auto_connect"].get(str(after.channel.id), None)
            ):
                voice_channel = after.channel
                text_channel_id = server_settings[str(member.guild.id)]["auto_connect"].get(str(after.channel.id), None)
                text_channel = member.guild.get_channel(text_channel_id)

                print (f"Voice Channel: {voice_channel}, Text Channel: {text_channel}")

                # チャンネルが存在しない場合はスキップ
                if not voice_channel or not text_channel:
                    return

                # 設定されているボイスチャンネルに人間が1人参加したとき
                if voice_channel.members and not all(member.bot for member in voice_channel.members):
                    voice_client = await voice_channel.connect()
                    await voice_client.guild.change_voice_state(channel=voice_channel, self_mute=False, self_deaf=True)
                    joined_text_channels[member.guild.id] = text_channel.id
                    if server_settings[str(member.guild.id)].get('join_leave_notification', SERVER_DEFAULT['join_leave_notification']):
                        await text_channel.send(f":inbox_tray:`{member.display_name}(@{member.name})`がボイスチャンネルに参加しました。")
                    embed = EMBED_DEFAULT.copy()
                    embed.title = ":speech_balloon:自動参加"
                    embed.description = "ボイスチャンネルに自動で参加しました。"
                    await text_channel.send(embed=embed)
        
        if voice_client and ((before.channel and before.channel.id == voice_client.channel.id) or (after.channel and after.channel.id == voice_client.channel.id)):
            text_channel=bot.get_channel(joined_text_channels.get(member.guild.id))

            # 設定が有効な場合、ボイスチャンネルの参加・退出・移動を検知
            if server_settings[str(member.guild.id)].get('join_leave_notification', SERVER_DEFAULT['join_leave_notification']):                    

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
                    text=parse_message(text)
                    await vp_play(bot, text, member.guild, bot.user)

            # ボイスチャンネルに参加者がいない場合、設定に応じて自動で退出する
            if server_settings[str(member.guild.id)].get("auto_disconnect", SERVER_DEFAULT["auto_disconnect"]):
                if voice_client.channel.members and all(member.bot for member in voice_client.channel.members):
                    await voice_client.disconnect()
                    embed = EMBED_DEFAULT.copy()
                    embed.title = ":zzz:自動退出"
                    embed.description = "参加者がいなくなったため、ボイスチャンネルから自動で退出しました。"
                    await text_channel.send(embed=embed)

                    joined_text_channels.pop(member.guild.id, None)
                    return
        

async def setup(bot):
    await bot.add_cog(VCConnection(bot))