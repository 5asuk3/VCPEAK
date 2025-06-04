import logging
import re
import requests
import emoji
from bs4 import BeautifulSoup

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
    text = emoji.demojize(text)
    return text

def parse_message(text):
    # URLの置換
    text = replace_url(text)
    # 絵文字の置換
    text = replace_emoji(text)
    if len(text) > 135:
        text = text[:135] + "、以下略。"

    return text