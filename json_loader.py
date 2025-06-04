import os
import json

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 設定の読み込み
data = load_json("config.json")
config=data['config']

user_default=data['user_default']
server_default=data['server_default']

user_settings = load_json("users.json")
server_settings = load_json("servers.json")
dict=load_json("dict.json")

TOKEN= config['discord_token']  # config.jsonからトークンを取得
VOICEPEAK_PATH=config['voicepeak_path']  # Voicepeakの実行ファイルのパス