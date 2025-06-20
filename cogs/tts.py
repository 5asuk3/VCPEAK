from discord.ext import commands
from config import joined_text_channels
from message_parser import pre_parse_message, parse_message
from vp_service import vp_play


class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # TTS Event
    @commands.Cog.listener()
    async def on_message(self, message):
        bot = self.bot
        # コマンドは読み上げない
        ctx = await bot.get_context(message)
        if ctx.valid:
            return
        
        # BotのメッセージとVCに参加していない場合は無視
        if (message.author.bot 
            or message.guild.id not in joined_text_channels
            or message.channel.id != joined_text_channels[message.guild.id]
        ):
            return
        
        # ボイスチャンネルに接続している場合のみ読み上げ
        voice_client = message.guild.voice_client
        if voice_client:
            text = pre_parse_message(message)
            text = parse_message(text)
            await vp_play(bot, text, message.guild, message.author)



async def setup(bot):
    await bot.add_cog(TTS(bot))