import os
import subprocess

def synthesize_voicepeak(voicepeak_path: str, output_path: str, text: str, narrator: str="", emotion: str="") -> bytes:
    """
    Voicepeakコマンドラインで音声合成を行う関数

    :param text: 合成するテキスト
    :param output_path: 出力する音声ファイルのパス（例: "output.wav"）
    :param voicepeak_path: voicepeak実行ファイルのパス（デフォルトは"voicepeak"）
    """
    cmd = [
        voicepeak_path,
        "-s", text,
        "-n", narrator,
        "-e", emotion,
        "-o", output_path
    ]
    try:
        result = subprocess.run(cmd, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Voicepeak音声合成に失敗しました: {e}")
        raise