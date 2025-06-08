import os
import json
from discord.ext import commands
from config import EMBED_COLOR_ERROR, EMBED_DEFAULT


def load_json(filename):
    filename="data/"+filename
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    filename="data/"+filename
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def is_owner_or_admin():
    async def predicate(ctx):
        return (
            await ctx.bot.is_owner(ctx.author)
            or (ctx.author.guild_permissions and ctx.author.guild_permissions.administrator)
        )
    return commands.check(predicate)


async def handle_check_fauilure(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = EMBED_DEFAULT.copy()
        embed.title = "権限エラー"
        embed.description = "このコマンドを実行する権限がありません。"
        embed.color = EMBED_COLOR_ERROR
        await ctx.send(embed=embed, ephemeral=True)
        return True
    return False