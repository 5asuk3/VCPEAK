VOICEPEAKを用いたDiscord用のテキスト読み上げボットです。  
まだ開発中のためバグが発生する可能性があります。issueを立ててくれるとうれしいです。

# コマンド
従来のチャットベースのコマンドのほか、スラッシュコマンドにも対応しているため、以下はすべてスラッシュコマンドを基準として書いています。  
もちろん`config.json`で設定されたprefixを使用したコマンドも対応しています。(デフォルト値は`!`)

### /help
簡略化されたコマンドリストが表示されます

### /connect
コマンドを実行したユーザーが参加しているボイスチャンネルにBotが参加し、以後そのチャンネルでテキストを読み上げます。

### /disconnect
ボイスチャンネルから切断します。

### /voice-list
現在利用可能なキャラクター一覧と、その感情一覧を表示します。

### /config list
コマンドを実行したユーザーの設定を表示します。

### /config narrator [キャラクター名]
読み上げるキャラクター（ナレーター）を設定します。省略時はデフォルト値が設定されます。

### /config emotion [感情名] [値]
読み上げ時の感情パラメータを設定します。感情名は省略できません。値省略時はその感情は0に設定されます。

### /config speed [速度(50～200)]
読み上げ速度を設定します。省略時はデフォルト値が設定されます。

### /config pitch [ピッチ(-300～300)]
読み上げピッチを設定します。省略時はデフォルト値が設定されます。

### /config randomize
キャラクター・感情・速度・ピッチをランダムに設定します。

### /config reset
ユーザー設定をデフォルト値にリセットします。

### /dict list
ことばリスト(辞書)に登録されている単語と読みを一覧表示します。

### /dict add [単語] [読み]
ことばリストに新しい単語とその読みを追加します。

### /dict delete [単語]
ことばリストから指定した単語を削除します。

### /server-config list
サーバーごとの設定を表示します。

### /server-config volume [音量(0～200)]
ボイスチャンネルの読み上げ音量を設定します。省略時はデフォルト値が設定されます。

### /server-config reset
サーバー設定をデフォルト値にリセットします。

<!--
まだ未完成なのでコメントアウト

# Linux環境でのインストール
## 動作確認環境
Ubuntu 24.04 LTSにて動作確認

## 前提のインストール
```
    # Debian系環境なら
    apt update && apt install -y ffmpeg curl
    python3 -m venv .venv
    source ./.venv/bin/activate
    ./.venv/bin/pip3 install -r requrements.txt
```

## VOICEPEAKのインストール
もしVOICEPEAKをまだインストールしていないのであれば新規でインストールする必要があります。
公式サイトにインストーラーが公開されているのでそれを利用します。
また、インストールにはGUI環境が必要です。詳細は気が向いたら書きます。
```
    mkdir temp && cd temp
    curl -O https://www.ah-soft.com/voice/setup/voicepeak-downloader-linux64
    chmod +x ./voicepeak-downloader-linux64
    ./voicepeak-downloader-linux64
```

ダウンロード先を指定するGUIが開きます。引数等で保存フォルダを前もって指示することは出来ないようです。
VOICEPEAKのライセンスを要求されるので準備しておきましょう。
```
    # tempファイル直下にダウンロードしたと仮定する
    unzip ./Voicepeak-linux64.zip -d ../lib
    cd ../
    ./lib/Voicepeak/voicepeak
```

VOICEPEAK本体がGUIで起動し、ダウンロード時にアクティベートしたボイスのインストール・他のライセンスのアクティベートなどが行えます。
ボイスのインストールが完了したら閉じてしまって問題ありません。

## 初期設定
初回起動前に`config.json`ファイルを編集してvoicepeak実行ファイルへのパスとdiscordトークンを貼り付ける必要があります。

        cp config.example.json config.json
```
    {
        "config":{
            "discord_token":"DISCORD TOKEN HERE",
            "voicepeak_path":"VOICEPEAK PATH HERE",
            "prefix":"!"
        },
        ...
    }
```

## 起動
    source ./.venv/bin/activate

    ./.venv/bin/python3 main.py
-->