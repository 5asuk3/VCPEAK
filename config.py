from json_loader import load_json
import subprocess

# 設定の読み込み
data = load_json("config.json")
config=data['config']
TOKEN= config['discord_token']  # config.jsonからトークンを取得
VOICEPEAK_PATH=config['voicepeak_path']  # Voicepeakの実行ファイルのパス
PREFIX=config['prefix']  # コマンドのプレフィックス

user_default=data['user_default']
server_default=data['server_default']

user_settings = load_json("users.json")
server_settings = load_json("servers.json")
dict=load_json("dict.json")

narrators = []
emotions = {}
try:
    result = subprocess.run([VOICEPEAK_PATH, "--list-narrator"], check=True, stdout=subprocess.PIPE, text=True)
    narrators=result.stdout.strip().splitlines()
except subprocess.CalledProcessError as e:
    print(f"話者取得に失敗しました: {e}")
    raise
for narrator in narrators:
    try:
        result = subprocess.run([VOICEPEAK_PATH, "--list-emotion", narrator], check=True, stdout=subprocess.PIPE, text=True)
        emotions[narrator] = result.stdout.strip().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"感情の取得に失敗しました: {e}")

for narrator in narrators:
    print(f"ナレーター: {narrator}, 感情: {emotions[narrator]}")
print(server_settings)
print(user_settings)