import logging
import re
import requests
import emoji
import unicodedata
from bs4 import BeautifulSoup
from config import dict, dict_pattern

def get_url_title(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "タイトルなし"
        return title
    except Exception as e:
        logging.error(f"URLのタイトル取得に失敗: {url} - {e}")
        return "タイトル取得失敗"
    
def replace_url(text):
    url_pattern = r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+'
    def replace(match):
        url = match.group(0)
        title = get_url_title(url)
        return f"『{title}』へのリンク"
    return re.sub(url_pattern, replace, text)

def replace_emoji(text):
    # カスタム絵文字の置換
    text = re.sub(r'<a?:([a-zA-Z0-9_]+):\d+>', r':\1:', text)
    # 通常の絵文字の置換
    text = emoji.demojize(text, language='ja')
    return text

def replace_word(text):
    # 辞書に基づいて単語を置換
    def repl(match):
        key= match.group(0)
        print(f"置換: {key} -> {dict.get(key, key)}")
        return dict.get(key, key)
    text = dict_pattern[0].sub(repl, text)

    # 半角文字を全角に変換(正規化)
    text = unicodedata.normalize('NFKC', text)
    return text


def parse_message(text):
    # URLの置換
    text = replace_url(text)
    # 絵文字の置換
    text = replace_emoji(text)

    text = replace_word(text)

    if len(text) > 135:
        text = text[:135] + "、以下略。"
    return text