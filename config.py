import re
import subprocess
from typing import Optional, Pattern
import discord
from utils import load_json


def update_dict_pattern():
    keys = [k for k in dictionary if k]  # 空文字列を除外
    dict_pattern[0] = re.compile("|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))) 


# 設定の読み込み
data = load_json("../config.json")
config=data['config']
TOKEN= config['discord_token']  # config.jsonからトークンを取得
VOICEPEAK_PATH=config['voicepeak_path']  # Voicepeakの実行ファイルのパス
PREFIX=config['prefix']  # コマンドのプレフィックス

USER_DEFAULT=data['user_default']
SERVER_DEFAULT=data['server_default']

user_settings = load_json("users.json")
server_settings = load_json("servers.json")
dictionary=load_json("dict.json")
dict_pattern: list[Optional[Pattern[str]]] = [None] # 辞書の正規表現パターンを格納するリスト（リストとして定義）
update_dict_pattern()

EMBED_COLOR_NORMAL = 0x4a913c  # デフォルトの埋め込みカラー
EMBED_COLOR_ERROR = 0xFF0000  # エラー用の埋め込みカラー
EMBED_DEFAULT = discord.Embed(
    title="VCPEAK",
    description="詳細な使い方は https://github.com/5asuk3/VCPEAK へ",
    color=EMBED_COLOR_NORMAL
)
EMBED_DEFAULT.set_footer(text="VCPEAK", icon_url="https://avatars.githubusercontent.com/5asuk3")

joined_text_channels={} # VC参加中のサーバーとチャンネル管理用の辞書

NARRATORS = []
EMOTIONS = {}
try:
    result = subprocess.run([VOICEPEAK_PATH, "--list-narrator"], check=True, stdout=subprocess.PIPE, text=True)
    NARRATORS=result.stdout.strip().splitlines()
except subprocess.CalledProcessError as e:
    print(f"話者取得に失敗しました: {e}")
    raise
for narrator in NARRATORS:
    try:
        result = subprocess.run([VOICEPEAK_PATH, "--list-emotion", narrator], check=True, stdout=subprocess.PIPE, text=True)
        EMOTIONS[narrator] = result.stdout.strip().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"感情の取得に失敗しました: {e}")
        raise

if USER_DEFAULT['narrator'] and USER_DEFAULT['narrator'] not in NARRATORS:
    print(f"ユーザーのデフォルトナレーター '{USER_DEFAULT['narrator']}' が利用可能なキャラクターの中に含まれていません。")
    exit(1)

if not isinstance(USER_DEFAULT['emotion'], (dict)):
    print("user_settingsのemotionキーの内容が不正です。辞書型である必要があります。")
    exit(1)
if USER_DEFAULT['emotion']:
    for emotion_name in USER_DEFAULT['emotion']:
        if emotion_name not in EMOTIONS.get(USER_DEFAULT['narrator'], []):
            print(f"ユーザーのデフォルト感情 '{emotion_name}' がナレーター '{USER_DEFAULT['narrator']}' の利用可能な感情の中に含まれていません。")
            exit(1)

print("設定の読み込みが完了しました。")
print(f"コマンドプレフィックス: {PREFIX}")
print(f"VOICEPEAKのパス: {VOICEPEAK_PATH}")