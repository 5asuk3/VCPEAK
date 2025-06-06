from discord import app_commands
from discord.ext import commands
from json_loader import save_json
from config import EMBED_DEFAULT, dictionary
from config import update_dict_pattern

class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dict_autocomplete(self, interaction, current: str):
        """ことばリストのオートコンプリート"""
        return [app_commands.Choice(name=word, value=word) for word in dictionary if current.lower() in word.lower()]

    # Dictionary Commands
    @commands.hybrid_group(name="dict")
    async def dict_config(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.show_dict(ctx)

    @dict_config.command(name="list", description="ことばリストの内容を表示")
    async def show_dict(self, ctx):
        """ことばリストの内容を表示"""
        embed= EMBED_DEFAULT.copy()
        embed.title = "ことばリスト"
        embed.description = "ことば一覧です。以下の単語は、読み上げ時に置き換えられます。"
        for key, value in dictionary.items():
            embed.add_field(name=key, value=f"⤷{value}", inline=True)
        
        await ctx.send(embed=embed)

    @dict_config.command(name="add", description="ことばリストに単語を追加")
    async def add_word(self, ctx, from_word: str, to_word: str):
        """ことばリストに単語を追加"""
        embed= EMBED_DEFAULT.copy()
        embed.title = "ことばリスト"

        if from_word in dictionary:
            embed.description = f"単語「{from_word}」はすでに存在します。"
            await ctx.send(embed=embed)
            return
        
        dictionary[from_word] = to_word
        save_json("dict.json", dictionary)
        update_dict_pattern()  # ことばリストのパターンを更新
        embed.description = f"単語「{from_word}」をことばリストに追加しました。読み: {to_word}"
        await ctx.send(embed=embed)

    @dict_config.command(name="delete", description="ことばリストから単語を削除")
    @app_commands.autocomplete(word=dict_autocomplete)
    async def delete_word(self, ctx, word: str):
        """ことばリストから単語を削除"""
        embed= EMBED_DEFAULT.copy()
        embed.title = "ことばリスト"

        if word not in dictionary:
            embed.description = f"単語「{word}」はことばリストに存在しません。"
            await ctx.send(embed=embed)
            return
        
        del dictionary[word]
        save_json("dict.json", dictionary)
        update_dict_pattern()  # ことばリストのパターンを更新
        embed.description = f"単語「{word}」をことばリストから削除しました。"
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Dictionary(bot))