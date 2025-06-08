import random
from discord import app_commands
from discord.ext import commands
from utils import save_json
from config import EMBED_DEFAULT, EMBED_COLOR_ERROR, user_settings, USER_DEFAULT, NARRATORS, EMOTIONS


class UserConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def ensure_user_settings(self, user_id):
        if user_id not in user_settings:
            user_settings[user_id] = USER_DEFAULT.copy()
            save_json("users.json", user_settings)
            

    async def narrator_autocomplete(self, interaction, current: str):
        """キャラクターのオートコンプリート"""
        return [app_commands.Choice(name=narrator, value=narrator) for narrator in NARRATORS if current.lower() in narrator.lower()]


    async def emotion_autocomplete(self, interaction, current: str):
        """感情のオートコンプリート"""
        narrator= interaction.user_settings.get('narrator')
        if narrator not in NARRATORS:
            print(f"無効なキャラクター: {narrator}")
            return []
        return [app_commands.Choice(name=emotion, value=emotion) for emotion in EMOTIONS[narrator] if current.lower() in emotion.lower()]


    # Config Commands
    @commands.hybrid_group(name="config", description="ユーザー設定")
    async def user_config(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.show_user_config(ctx)


    @user_config.command(name="show", description="ユーザー設定を表示")
    async def show_user_config(self, ctx):
        """ユーザー設定を表示"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"
        embed.description = "/config reset でデフォルト値にリセットできます。"

        #TODO不正な値のものがあったらデフォルト値に戻す
        user_id = str(ctx.author.id)
        self.ensure_user_settings(user_id)
        settings = user_settings[user_id]
        embed.add_field(name="キャラクター", value=settings['narrator'], inline=False)
        embed.add_field(name="感情", value=", ".join(f"**{emotion}**:{value}" for emotion, value in settings['emotion'].items()), inline=False)
        embed.add_field(name="速度", value=settings['speed'], inline=True)
        embed.add_field(name="ピッチ", value=settings['pitch'], inline=True)
        
        await ctx.send(embed=embed)
        

    @user_config.command(name="narrator", description="キャラクターを設定")
    @app_commands.autocomplete(narrator=narrator_autocomplete)
    async def set_narrator(self, ctx, narrator: str=USER_DEFAULT['narrator']):
        """キャラクターを設定"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"

        user_id = str(ctx.author.id)
        self.ensure_user_settings(user_id)
        if narrator not in NARRATORS:
            embed.description = f"引数がない、もしくは無効なキャラクターです。\n利用可能なキャラクター: {', '.join(NARRATORS)}"
            embed.color = EMBED_COLOR_ERROR
            await ctx.send(embed=embed)
            return
        
        user_settings[user_id]["narrator"] = narrator
        user_settings[user_id]["emotion"]={emotion_name: 0 for emotion_name in EMOTIONS[narrator]}
        save_json("users.json", user_settings)
        embed.description = f"キャラクターを「{narrator}」に設定しました。(感情設定はデフォルト値にリセットされました)"
        await ctx.send(embed=embed)


    @app_commands.autocomplete(emotion=emotion_autocomplete)
    @user_config.command(name="emotion", description="感情を設定")
    async def set_emotion(self, ctx, emotion: str="", value: int=0):
        """感情を設定"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"

        user_id = str(ctx.author.id)
        self.ensure_user_settings(user_id)
        narrator= user_settings[user_id]["narrator"]
        if emotion not in EMOTIONS.get(narrator, []):
            embed.description = f"引数がない、もしくは無効な感情です。\n{narrator}が利用可能な感情: {', '.join(EMOTIONS.get(narrator, []))}"
            embed.color = EMBED_COLOR_ERROR
            await ctx.send(embed=embed)
            return
        #TODO不正な値のものがあったらデフォルト値に戻す
        if value < 0 or value > 100:
            embed.description = "感情の値は0から100の範囲で設定してください。"
            embed.color = EMBED_COLOR_ERROR
            await ctx.send(embed=embed)
            return
        user_settings[user_id]["emotion"][emotion] = value
        save_json("users.json", user_settings)
        
        embed.description = f"感情「{emotion}」を{value}%に設定しました。"
        await ctx.send(embed=embed)


    @user_config.command(name="speed", description="音声の速度を設定")
    async def set_speed(self, ctx, speed: int=USER_DEFAULT['speed']):
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"

        if speed < 50 or speed > 200:
            await ctx.send("速度は50から200の範囲で設定してください。")
            embed.color = EMBED_COLOR_ERROR
            return
        
        user_id = str(ctx.author.id)
        self.ensure_user_settings(user_id)
        user_settings[user_id]["speed"] = speed
        save_json("users.json", user_settings)

        embed.description = f"音声の速度を{speed}%に設定しました。"
        await ctx.send(embed=embed)


    @user_config.command(name="pitch", description="音声のピッチを設定")
    async def set_pitch(self, ctx, pitch: int=USER_DEFAULT['pitch']):
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"
        
        if pitch < -300 or pitch > 300:
            embed.description = "ピッチは-300から300の範囲で設定してください。"
            embed.color = EMBED_COLOR_ERROR
            await ctx.send(embed=embed)
            return
        
        user_id = str(ctx.author.id)
        self.ensure_user_settings(user_id)
        user_settings[user_id]["pitch"] = pitch
        save_json("users.json", user_settings)
        
        embed.description = f"音声のピッチを{pitch}%に設定しました。"
        await ctx.send(embed=embed)


    @user_config.command(name="randomize", description="キャラクターや感情をランダムに設定")
    async def randomize_user_config(self, ctx):
        """キャラクターや感情をランダムに設定"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"

        user_id = str(ctx.author.id)
        self.ensure_user_settings(user_id)
        
        # ランダムなキャラクターを選択
        narrator = random.choice(NARRATORS)
        user_settings[user_id]["narrator"] = narrator
        
        # ランダムな感情を選択
        emotions = EMOTIONS[narrator]
        user_settings[user_id]["emotion"] = {emotion: random.randint(0, 100) for emotion in emotions}
        
        # ランダムな速度とピッチを設定
        user_settings[user_id]["speed"] = random.randint(50, 200)
        user_settings[user_id]["pitch"] = random.randint(-300, 300)
        
        save_json("users.json", user_settings)
        
        
        embed.description = "各種設定をランダムに設定しました。"
        await ctx.send(embed=embed)
        await self.show_user_config(ctx)  # 設定内容を表示


    @user_config.command(name="reset", description="ユーザー設定をデフォルトにリセット")
    async def reset_user_config(self, ctx):
        """ユーザー設定をデフォルトにリセット"""
        embed= EMBED_DEFAULT.copy()
        embed.title = f"{ctx.author.display_name}のユーザー設定"
        embed.description = "ユーザー設定をデフォルト値にリセットしました。"

        user_id = str(ctx.author.id)
        user_settings[user_id] = USER_DEFAULT.copy()
        save_json("users.json", user_settings)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UserConfig(bot))