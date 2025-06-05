import os
import asyncio
import tempfile
import collections
import discord
from vp_wrapper import synthesize_vp
from config import VOICEPEAK_PATH, server_settings, user_settings, USER_DEFAULT, NARRATORS, EMOTIONS

voice_queue = collections.defaultdict(asyncio.Queue)
playing_flags = collections.defaultdict(lambda: False)  # 再生中フラグ

async def vp_play(bot, text, guild, user):
    await voice_queue[guild.id].put((text, user.id))
    if not playing_flags[guild.id]:
        await vp_play_next(bot, guild)

async def vp_play_next(bot, guild):
    playing_flags[guild.id]=True
    try:
        voice_client=guild.voice_client
        if not voice_client:
            return
        
        queue=voice_queue[guild.id]
        while not queue.empty():
            contents=await queue.get()
            text, user_id=contents
            user_set=user_settings.get(str(user_id), USER_DEFAULT.copy())
            if user_set['narrator'] !=USER_DEFAULT['narrator'] and user_set['narrator'] not in NARRATORS:
                user_set['narrator'] = USER_DEFAULT['narrator']
                user_set["emotion"]={emotion_name: 0 for emotion_name in EMOTIONS[user_set['narrator']]}
            parsed_emotion = ", ".join(f"{emotion_name}={value}" for emotion_name, value in user_set['emotion'].items())

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path=tmp.name

            await asyncio.to_thread(
                synthesize_vp,
                VOICEPEAK_PATH,
                text,
                tmp_path,
                user_set['narrator'],
                parsed_emotion,
                user_set['speed'],
                user_set['pitch']                
            )

            source = discord.FFmpegPCMAudio(tmp_path)
            vol=server_settings[str(guild.id)].get('volume')/100
            source = discord.PCMVolumeTransformer(source, volume=vol)

            play_finished=asyncio.Event()

            def after_play(e):
                try:
                    os.remove(tmp_path)
                except Exception as ex:
                    print(f"一時ファイル削除エラー: {ex}")
                if e:
                    print(f"再生時エラー: {e}")
                        # 次の音声を再生
                bot.loop.call_soon_threadsafe(play_finished.set)

            voice_client.play(source, after=after_play)
            await play_finished.wait()
    finally:
        playing_flags[guild.id]=False