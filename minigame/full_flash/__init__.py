import discord
import copy
import random
import asyncio
from config import client, MINIGAME_CHANNEL_ID
from minigame.minigame import Minigame

def is_winning_hand(hand, meld=4, eye=1):
    if meld == 0 and eye == 0:
        return True
    if meld > 0:
        for i in range(9):
            if hand[i] >= 3:
                nhand = copy.copy(hand)
                nhand[i] -= 3
                if is_winning_hand(nhand, meld-1, eye):
                    return True
        for i in range(7):
            if hand[i] >= 1 and hand[i+1] >= 1 and hand[i+2] >= 1:
                nhand = copy.copy(hand)
                nhand[i] -= 1
                nhand[i+1] -= 1
                nhand[i+2] -= 1
                if is_winning_hand(nhand, meld-1, eye):
                    return True
    if eye > 0:
        for i in range(9):
            if hand[i] >= 2:
                nhand = copy.copy(hand)
                nhand[i] -= 2
                if is_winning_hand(nhand, meld, eye-1):
                    return True
    return False

def add_random_chow(hand):
    chow_list = []
    for i in range(7):
        if hand[i] <= 3 and hand[i+1] <= 3 and hand[i+2] <= 3:
            chow_list.append(i)
    chow_begin = random.choice(chow_list)
    for i in range(3):
        hand[chow_begin+i] += 1

def add_random_pong(hand):
    pong_list = []
    for i in range(9):
        if hand[i] <= 1:
            pong_list.append(i)
    pong = random.choice(pong_list)
    hand[pong] += 3

def add_random_eye(hand):
    eye_list = []
    for i in range(9):
        if hand[i] <= 2:
            eye_list.append(i)
    eye = random.choice(eye_list)
    hand[eye] += 2

def generate_quiz():
    hand = [0 for _ in range(9)]
    for _ in range(4):
        if random.randrange(4) == 0:
            add_random_pong(hand)
        else:
            add_random_chow(hand)
    add_random_eye(hand)
    eliminate_list = []
    for i in range(9):
        if hand[i] > 0:
            eliminate_list.append(i)
    hand[random.choice(eliminate_list)] -= 1
    ans = set()
    for i in range(9):
        if hand[i] <= 3:
            nhand = copy.copy(hand)
            nhand[i] += 1
            if is_winning_hand(nhand):
                ans.add(i)
    return (hand, ans)

class FullFlash(Minigame):
    def commands(self) -> list[str]:
        return ["清一色クイズ", "清一色", "チンイツクイズ", "チンイツ", "chinitsu"]

    def help(self) -> str:
        return\
            "麻雀の清一色の待ちを当てるゲームです 🀄\n"\
            "清一色聴牌の局面が与えられるので、待ち牌を過不足なく答えてください"

    def help_detail(self) -> str:
        return\
            f"{self.help()}\n\n"\
            "最初に清一色聴牌の局面が理牌されていない状態で与えられます\n"\
            "  例: `4 8 3 2 5 5 5 6 3 7 6 4 5`\n"\
            "30 秒経過で理牌されます\n"\
            "  例: `2 3 3 4 4 5 5 5 5 6 6 7 8`\n"\
            "さらに 30 秒経過すると待ちの種類数を教えてくれます\n"\
            "  例: 6種\n"\
            "答えが分かったタイミングで、待ち牌の数字を過不足なく答えられたらクリアです！\n"\
            "  例: `134679`"

    async def play(self, args: list[str]) -> None:
        minigame_channel = client.get_channel(MINIGAME_CHANNEL_ID)
        thread = await minigame_channel.create_thread(name="清一色クイズ", type=discord.ChannelType.public_thread)
        hand, ans = generate_quiz()
        hand_list = []
        for i in range(9):
            hand_list += [str(i+1) for _ in range(hand[i])]
        hand_str = " ".join(hand_list)
        random.shuffle(hand_list)
        hand_str_shuffled = " ".join(hand_list)
        ans_list = [str(wait+1) for wait in ans]
        ans_list.sort()
        messages = [
            "分からない？...じゃあ理牌してあげる～ 😉\n**" + hand_str + "**",
            "まだ分からない？しょうがないなあ... 🙂‍↔️\nこの待ちは**" + str(len(ans)) + "**種あるよ～",
            "残念...時間切れです 😇\n正解は**" + ", ".join(ans_list) + "**待ちでした！"
        ]
        async def wait_for_correct_ans():
            while True:
                ans_message = await client.wait_for("message")
                if ans_message.author.bot or ans_message.channel != thread:
                    continue
                user_ans = set()
                for i in range(9):
                    if str(i+1) in ans_message.content:
                        user_ans.add(i)
                if user_ans == ans:
                    await thread.send(ans_message.author.mention + "正解 👏 (**" + ", ".join(ans_list) + "**待ち)")
                    await ans_message.add_reaction("👍")
                    return
                else:
                    await ans_message.add_reaction("🙅")
        await thread.send(
            "__**清一色クイズ**__ 🀄\n"\
            "この清一色、何待ち？\n"\
            "(30 秒経過で理牌するよ～)\n"\
            f"**{hand_str_shuffled}**"
        )
        for i in range(len(messages)):
            try:
                await asyncio.wait_for(wait_for_correct_ans(), timeout=30)
            except asyncio.TimeoutError:
                await thread.send(messages[i])