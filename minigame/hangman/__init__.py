import discord
import random
import requests
import asyncio
from enum import IntEnum
import re
from config import client, MINIGAME_CHANNEL_ID
from minigame.minigame import Minigame

MIN_LEN = 6
DIFFICULTY_THRESHOLD = [10000, 5000, 1000]
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ALPHABET_RUSSIAN = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"

class Level(IntEnum):
    NORMAL = 0
    HARD = 1
    EXTREME = 2
    MAX = 3
    RUSSIAN = 4

class Hangman(Minigame):
    def __init__(self) -> None:
        f = open("minigame/hangman/words.txt", "r")
        lines = f.read().split("\n")
        f.close()
        self.words: list[list[str]] = [[] for _ in range(5)]
        pattern = re.compile(f'"([{ALPHABET}]+)","([0-9]+)"')
        for line in lines:
            m = pattern.match(line)
            if m is not None and len(m.groups()) >= 2:
                word = m.group(1).lower()
                frequency = int(m.group(2))
                if len(word) < MIN_LEN:
                    continue
                if frequency >= DIFFICULTY_THRESHOLD[0]:
                    self.words[Level.NORMAL].append(word)
                elif frequency >= DIFFICULTY_THRESHOLD[1]:
                    self.words[Level.HARD].append(word)
                elif frequency >= DIFFICULTY_THRESHOLD[2]:
                    self.words[Level.EXTREME].append(word)
                else:
                    self.words[Level.MAX].append(word)
        f = open("minigame/hangman/words_russian.txt", "r")
        lines = f.read().split("\n")
        f.close()
        pattern = re.compile(f"([{ALPHABET_RUSSIAN}]+)")
        for line in lines:
            m = pattern.match(line)
            if m is not None and len(m.groups()) >= 1:
                word = m.group(1).lower()
                if len(word) >= MIN_LEN:
                    self.words[Level.RUSSIAN].append(word)

    def commands(self) -> list[str]:
        return ["hangman"]
    
    def help(self) -> str:
        return\
            "単語に含まれると思われる文字を 1 つずつ選びながら単語を当てるゲームです 🔠\n"\
            "オプション引数として難易度 (hard, extreme, max) を与えることもできます\n"\
            "引数に russian を指定するとロシア語バージョンになります 🇷🇺"
    
    def help_detail(self) -> str:
        return\
            f"{self.help()}\n\n"\
            "以下のようにゲームを進めていきます:\n"\
            "- 単語に含まれると思われる文字を 1 文字答える\n"\
            "  - 例: `x`\n"\
            "  - 実際にその文字が単語に含まれていれば何文字目にあるかがすべてオープンされ、含まれていなければ残機が 1 減ります\n"\
            "- 単語そのものを予想する\n"\
            "  - 例: `word`\n"\
            "  - 合っていれば単語全体がオープンされ、合っていなければ残機が 1 減ります\n"\
            "残機が 0 になる前に単語のすべての文字をオープンできればクリアです！"

    async def play(self, args: list[str]) -> None:
        minigame_channel = client.get_channel(MINIGAME_CHANNEL_ID)
        thread = await minigame_channel.create_thread(name="Hangman", type=discord.ChannelType.public_thread)
        level: Level = Level.NORMAL
        if len(args) > 0:
            if args[0].lower() == "hard":
                level = Level.HARD
            elif args[0].lower() == "extreme":
                level = Level.EXTREME
            elif args[0].lower() == "max":
                level = Level.MAX
            elif args[0].lower() == "russian":
                level = Level.RUSSIAN
        word = random.choice(self.words[level])
        life = 6
        opened = [False for _ in range(len(word))]
        chars = ""
        if level != Level.RUSSIAN:
            alphabet = ALPHABET
            try:
                data = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + word).json()[0]
            except:
                data = {}
            description = "**" + word + "**"
            if "phonetic" in data:
                description += " " + data["phonetic"]
            else:
                description += " (phonetic not found)"
            if "meanings" in data:
                for meaning in data["meanings"]:
                    description += "\n__" + meaning["partOfSpeech"] + "__"
                    for definition in meaning["definitions"]:
                        description += "\n- " + definition["definition"]
            else:
                description += "\n(meanings not found)"
            if "sourceUrls" in data:
                description += "\nsource:"
                for source in data["sourceUrls"]:
                    description += "\n- " + source
            else:
                description += "\n(source not found)"
        else:
            alphabet = ALPHABET_RUSSIAN
            description = ""
        await thread.send(
            (
                "__**Hangman**__ 🔠\n" if level == Level.NORMAL else
                "__**Hangman hard**__ 💥\n" if level == Level.HARD else
                "__**Hangman extreme**__ 🔥\n" if level == Level.EXTREME else
                "__**Hangman max**__ 👹\n" if level == Level.MAX else
                "__**Hangman Russian**__ 🇷🇺\n"
            ) +
            (
                "ロシア語の単語を当てよう！\n" if level == Level.RUSSIAN else
                "英単語を当てよう！\n"
            ) +
            "答え方:\n"\
                "- アルファベット 1 種類を開ける\n"\
                "- 単語を丸ごと答える"
        )
        def check(ans_message):
            if ans_message.channel != thread:
                return False
            for c in ans_message.content:
                if not c in alphabet:
                    return False
            return True
        while life > 0:
            blank = "\\_"
            await thread.send(
                f"現在の状態: **{' '.join([(word[i] if opened[i] else blank) for i in range(len(word))])}**\n"\
                f"残機: {str(life)}\n"\
                f"使った文字: {' '.join([(f'**{char}**' if char in word else char) for char in chars])}"
            )
            try:
                ans_message = await client.wait_for("message", check=check, timeout=180)
                if len(ans_message.content) == 1:
                    char = ans_message.content.lower()
                    if char in chars:
                        await thread.send("その文字は既出です 🤔")
                    else:
                        for i in range(len(word)):
                            if word[i] == char:
                                opened[i] = True
                        chars += char
                        if not char in word:
                            life -= 1
                        if not False in opened:
                            await thread.send(ans_message.author.mention + "正解 👏 (**" + word + "**)")
                            await ans_message.add_reaction("👍")
                            break
                else:
                    predict = ans_message.content.lower()
                    if predict == word:
                        await thread.send(ans_message.author.mention + "正解 👏 (**" + word + "**)")
                        await ans_message.add_reaction("👍")
                        break
                    else:
                        life -= 1
            except asyncio.TimeoutError:
                await thread.send("3分間無言だったので終了するよ 👋\n正解は**" + word + "**でした！")
                break
        if life == 0:
            await thread.send("残念... 😇\n正解は**" + word + "**でした！")
        if level != Level.RUSSIAN:
            await thread.send(description)