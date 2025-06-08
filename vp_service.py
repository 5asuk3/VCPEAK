import os
import asyncio
import tempfile
import collections
import discord
from vp_wrapper import synthesize_vp
from config import VOICEPEAK_PATH, server_settings, user_settings, SERVER_DEFAULT, USER_DEFAULT, NARRATORS, EMOTIONS, joined_text_channels, EMBED_DEFAULT

synthesis_queue = collections.defaultdict(asyncio.Queue) # 音声合成キュー
play_queue = collections.defaultdict(asyncio.Queue)  # 再生キュー
playing_flags = collections.defaultdict(lambda: False)  # 再生中フラグ
synthesis_flags = collections.defaultdict(lambda: False)  # 音声合成中フラグ
synthesize_lock = asyncio.Lock()  # 音声合成のロック


async def vp_play(bot, text, guild, user):
    await synthesis_queue[guild.id].put((text, user.id))
    if not synthesis_flags[guild.id]:
         bot.loop.create_task(vp_synthesis_worker(bot, guild))

async def vp_synthesis_worker(bot, guild):
    synthesis_flags[guild.id] = True
    try:
        queue = synthesis_queue[guild.id]
        while not queue.empty():
            text, user_id=await queue.get()
            user_set=user_settings.get(str(user_id), USER_DEFAULT.copy())
            if user_set['narrator'] != USER_DEFAULT['narrator'] and user_set['narrator'] not in NARRATORS:
                user_set['narrator'] = USER_DEFAULT['narrator']
                user_set["emotion"] = {emotion_name: 0 for emotion_name in EMOTIONS[user_set['narrator']]}
            joined_emotion = ", ".join(f"{emotion_name}={value}" for emotion_name, value in user_set['emotion'].items())

            retry_count = 0
            while retry_count < 3:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path=tmp.name
                
                # 音声合成を実行(VOICEPEAKが同時に1つしか実行できないため、ロックを使用)
                async with synthesize_lock:
                    result = await asyncio.to_thread(
                            synthesize_vp,
                            VOICEPEAK_PATH,
                            text,
                            tmp_path,
                            user_set['narrator'],
                            joined_emotion,
                            user_set['speed'],
                            user_set['pitch']
                        )
                
                if result == 0:        
                    await play_queue[guild.id].put(tmp_path)
                    if not playing_flags[guild.id]:
                      bot.loop.create_task(vp_play_work(bot, guild))
                    print (f"音声合成成功: {text}")
                    break
                else:
                    retry_count += 1
                    await asyncio.sleep(1)  # 少し待機してから次の処理へ
                    try:
                        os.remove(tmp_path)
                    except Exception as e:
                        print(f"一時ファイル削除エラー: {e}")
                    if retry_count >= 3:
                        channel = guild.get_channel(joined_text_channels[guild.id])
                        embed = EMBED_DEFAULT.copy()
                        embed.title = "音声合成エラー"
                        embed.description = f"音声合成に失敗しました。エラーコード: {result}"
                        embed.add_field(name="内容", value=text, inline=False)
                        await channel.send(embed=embed)

            queue.task_done()
    finally:
        synthesis_flags[guild.id] = False

async def vp_play_work(bot, guild):
    playing_flags[guild.id]=True
    try:
        queue=play_queue[guild.id]
        while True:
            tmp_path=await queue.get()
            voice_client=guild.voice_client
            # ボイスチャンネルが切断されている場合は終了
            if not voice_client:
                while not queue.empty():
                    try:
                        tmp_path=queue.get_nowait()
                        try:
                            os.remove(tmp_path)
                        except Exception as e:
                            print(f"一時ファイル削除エラー: {e}")
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        break
                break
            source = discord.FFmpegPCMAudio(tmp_path)
            vol=server_settings[str(guild.id)].get('volume', SERVER_DEFAULT['volume'])/100
            source = discord.PCMVolumeTransformer(source, volume=vol)

            play_finished=asyncio.Event()

            def after_play(e):
                try:
                    os.remove(tmp_path)
                except Exception as ex:
                    print(f"一時ファイル削除エラー: {ex}")
                if e:
                    print(f"再生時エラー: {e}")
                    queue.task_done()
                    # 次の音声を再生
                bot.loop.call_soon_threadsafe(play_finished.set)

            voice_client.play(source, after=after_play)
            await play_finished.wait()
            queue.task_done()
            if queue.empty():
                break
    finally:
        playing_flags[guild.id]=False