import discord
import random
import requests
import asyncio
from config import client, MINIGAME_CHANNEL_ID

COMMANDS = ["Hangman", "hangman"]

words = []

def init():
    f = open("minigame/hangman_words.txt", "r")
    global words
    words = f.read().split()
    f.close()

def choose_word():
    return random.choice(words)

async def play():
    minigame_channel = client.get_channel(MINIGAME_CHANNEL_ID)
    thread = await minigame_channel.create_thread(name="hangman", type=discord.ChannelType.public_thread)
    word = choose_word()
    life = len(word)
    opened = [False for _ in range(len(word))]
    chars = []
    try:
        data = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + word).json()[0]
    except:
        data = None
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
        description += "\nsource: " + " ".join(data["sourceUrls"])
    else:
        description += "\nsource not found"
    await thread.send("__**hangman**__ 🔠\n英単語を当てよう！\n答え方:\n- アルファベット1文字を開ける\n- 単語を丸ごと答える")
    def check(ans_message):
        if ans_message.channel != thread:
            return False
        for c in ans_message.content:
            if not ("a" <= c <= "z" or "A" <= c <= "Z"):
                return False
        return True
    while life > 0:
        await thread.send("現在の状態: **" + " ".join([(word[i] if opened[i] else "\\_") for i in range(len(word))]) + "**\n残機: " + str(life) + "\n使った文字: " + " ".join(chars))
        try:
            ans_message = await client.wait_for("message", check=check, timeout=180)
            if len(ans_message.content) == 1:
                char = ans_message.content.lower()
                for i in range(len(word)):
                    if word[i] == char:
                        opened[i] = True
                if char in word:
                    chars.append("**" + char + "**")
                else:
                    chars.append(char)
                    life -= 1
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
    await thread.send(description)