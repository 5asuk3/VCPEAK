from json_loader import load_json
import re
import subprocess

def update_dict_pattern():
    keys = [k for k in dict if k]  # 空文字列を除外
    dict_pattern[0] = re.compile("|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True)))
    print(dict_pattern[0].pattern)  # 正規表現パターンを表示

# 設定の読み込み
data = load_json("config.json")
config=data['config']
TOKEN= config['discord_token']  # config.jsonからトークンを取得
VOICEPEAK_PATH=config['voicepeak_path']  # Voicepeakの実行ファイルのパス
PREFIX=config['prefix']  # コマンドのプレフィックス

USER_DEFAULT=data['user_default']
SERVER_DEFAULT=data['server_default']

user_settings = load_json("users.json")
server_settings = load_json("servers.json")
dict=load_json("dict.json")
dict_pattern = [None]  # 辞書の正規表現パターンを格納するリスト
update_dict_pattern()


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

if USER_DEFAULT['narrator']!="" and USER_DEFAULT['narrator'] not in NARRATORS:
    print(f"ユーザーのデフォルトナレーター '{USER_DEFAULT['narrator']}' が利用可能なキャラクターの中に含まれていません。")
    exit(1)

print("設定の読み込みが完了しました。")
print(f"コマンドプレフィックス: {PREFIX}")
print(f"VOICEPEAKのパス: {VOICEPEAK_PATH}")

print("利用可能なキャラクター:")
for narrator in NARRATORS:
    print(f"\tナレーター: {narrator}\t感情: {', '.join(EMOTIONS[narrator])}")
print("サーバーのデフォルト設定:")
print(f"\t", ", ".join(f"{key}={value}" for key, value in SERVER_DEFAULT.items()))
print("ユーザーのデフォルト設定:")
print(f"\t", ", ".join(f"{key}={value}" for key, value in USER_DEFAULT.items()))