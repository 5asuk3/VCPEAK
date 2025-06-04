import subprocess

def synthesize_vp(voicepeak_path: str, text: str, output_path: str, narrator: str="", emotion: str="", speed: str="", pitch: str="") -> bytes:
    cmd = [
        voicepeak_path, 
        "-s", text, 
        "-o", output_path, 
        "--narrator", narrator, 
        "--emotion", emotion, 
        "--speed", str(speed), 
        "--pitch", str(pitch)
    ]

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Voicepeak音声合成に失敗しました: {e}")
        raise