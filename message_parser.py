import logging
import re
import discord
import emoji
import unicodedata
import requests
import alkana
import romkan
from bs4 import BeautifulSoup
from config import EMBEDED_DICTIONALY, dictionary, dict_pattern


def get_url_title(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "タイトルなし"
        return title[:20] + "、以下略。"
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
        for pattern, value in dictionary.items():
            if re.fullmatch(pattern, key, flags=re.IGNORECASE):
                # print(f"{pattern}を{value}に置換")
                return str(value)
        return key
    
    def repl_embed(match):
        key= match.group(0).lower()
        return str(EMBEDED_DICTIONALY.get(key, key))

    # 英語の単語をカタカナに変換
    def repl_eng(match):
        key= match.group(0)
        return str(alkana.get_kana(key) or key)

    # 辞書に基づいて単語を置換
    text = dict_pattern[1].sub(repl_embed, text) if dict_pattern[1] else text
    text = dict_pattern[0].sub(repl, text) if dict_pattern[0] else text
    # if dict_pattern[1]:
    #     print(f"dict_pattern[1] に一致する部分: {dict_pattern[1].findall(text)}")
    # if dict_pattern[0]:
    #     print(f"dict_pattern[0] に一致する部分: {dict_pattern[0].findall(text)}")

    # 英語の単語をカタカナに変換
    text = re.sub(r'[a-z]+|[A-Z][a-z]*', repl_eng, text)

    text = romkan.to_hiragana(text)  # ローマ字をひらがなに変換

    # 半角文字を全角に変換(正規化)
    text = unicodedata.normalize('NFKC', text)
    return text


# メンションやリンクを事前に解析
def pre_parse_message(message : discord.Message):
    mention_pattern = r'<@!?(\d+)>'
    channel_link_pattern = r'<#(\d+)>'
    message_link_pattern = r'https://discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)'
    
    def repl_men(match):
        user_id = int(match.group(1))
        member = message.guild.get_member(user_id) if message.guild else None
        if member:
            return f"{member.display_name}へのメンション"
        else:
            return "不明なユーザーへのメンション"

    def repl_ch(match):
        channel_id = int(match.group(1))
        channel = message.guild.get_channel(channel_id) if message.guild else None
        if channel:
            return f"{channel.name}へのリンク"
        else:
            return "不明なチャンネルへのリンク"
    
    def repl_msg(match):
        channel_id = int(match.group(2))
        channel = message.guild.get_channel(channel_id) if message.guild else None
        if channel:
            return f"{channel.name}へのリンク"
        else:
            return "不明なチャンネルへのリンク"

    def replace_ref(message :discord.Message):
        # メッセージの転送や返信を解析
        if message.reference:
            channel = message.guild.get_channel(message.reference.channel_id) if message.guild else None
            if channel:
                # 返信の場合
                if channel==message.channel:
                    resolved = message.reference.resolved
                    # 返信先のメッセージが削除されている場合
                    if isinstance(resolved,  discord.DeletedReferencedMessage):
                        return "削除されたメッセージへの返信"
                    member= message.guild.get_member(resolved.author.id) if message.guild and resolved else None
                    if member:
                        return f"{member.display_name}への返信"
                    else:
                        return "不明なユーザーへの返信"
                # 転送の場合
                return f"{channel.name}から転送"
            else:
                return "不明なチャンネルから転送"

    msg_componets = []
    # 返信・転送があれば追加
    if message.reference:
        msg_componets.append(replace_ref(message))
    # 本文があれば追加
    if message.content.strip():
        text = message.content
        text=re.sub(mention_pattern, repl_men, text)
        text=re.sub(channel_link_pattern, repl_ch, text)
        text=re.sub(message_link_pattern, repl_msg, text)
        msg_componets.append(text)
    # スタンプがあれば追加
    if message.stickers:
        msg_componets.append(f"{message.stickers[0].name}のスタンプ")
    # 添付ファイルがあれば追加
    if message.attachments:
        msg_componets.append(f"添付ファイルが送信されました")

    # スタンプと本文を結合・整形して返す
    return "、".join(msg_componets)


def parse_message(text):
    # URLの置換
    text = replace_url(text)
    # 絵文字の置換
    text = replace_emoji(text)
    # 辞書に基づいた置換・文字の正規化
    text = replace_word(text)

    if len(text) > 135:
        text = text[:135] + "、以下略。"
    return text