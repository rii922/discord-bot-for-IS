import discord
import requests
import re
from config import client, MINIGAME_CHANNEL_ID

COMMANDS = ["Akinator", "akinator", "AKINATOR", "アキネイター"]

class SessionFailure(Exception):
    pass

class QuestionFailure(Exception):
    pass

class NoMoreQuestions(Exception):
    pass

class InvalidCompletion(Exception):
    pass

class CantGoAnyFurther(Exception):
    pass

class Akinator:
    def __init__(self):
        self.question = None
        self.step = None
        self.progression = None
        self.step_last_proposition = None
        self.guessed = None
        self.guess_name = None
        self.guess_description = None
        self.guess_image = None
        self.uri = None
        self.akitude = None
        self.language = None
        self.child_mode = None
        self.session = None
        self.signature = None
    
    def _update(self, response):
        if "id_base_proposition" in response:
            self.step_last_proposition = self.step
            self.guessed = True
            self.guess_name = response["name_proposition"]
            self.guess_description = response["description_proposition"]
            self.guess_image = response["photo"]
        else:
            self.question = response["question"]
            self.step = int(response["step"])
            self.progression = float(response["progression"])
            self.akitude = response["akitude"]
    
    def start_game(self, language=None, child_mode=False):
        self.language = language
        self.child_mode = child_mode
        self.uri = f"https://{self.language}.akinator.com"
        self.akitude = "defi.png"
        url = f"{self.uri}/game"
        json = {"sid": 1, "cm": str(self.child_mode).lower()}
        response = requests.post(url, json=json)
        match_session = re.search(r"session:\s*'(.+)'", response.text)
        match_signature = re.search(r"signature:\s*'(.+)'", response.text)
        if match_session is None or match_signature is None:
            raise SessionFailure("connection error: failed to get session or signature")
        self.session = match_session.group(1)
        self.signature = match_signature.group(1)
        match_question = re.search(r"<p class=\"question-text\" id=\"question-label\">\s*(.+)\s*</p>", response.text)
        if match_question is None:
            raise QuestionFailure("connection error: failed to get question")
        self.question = match_question.group(1)
        self.step = 0
        self.progression = 0.0
        self.guessed = False
    
    def answer(self, ans):
        url = f"{self.uri}/answer"
        json = {"sid": 1, "cm": str(self.child_mode).lower(), "answer": ans, "step": self.step, "progression": self.progression, "step_last_proposition": self.step_last_proposition or "", "session": self.session, "signature": self.signature}
        response = requests.post(url, json=json).json()
        if response["completion"] == "SOUNDLIKE":
            raise NoMoreQuestions("maximum question error: no more questions to ask")
        if response["completion"] != "OK":
            raise InvalidCompletion(f"technical error: returned non-OK completion '{response['completion']}'")
        self._update(response)
    
    def exclude(self):
        self.guessed = False
        url = f"{self.uri}/exclude"
        json = {"sid": 1, "cm": str(self.child_mode).lower(), "step": self.step, "progression": self.progression, "session": self.session, "signature": self.signature}
        response = requests.post(url, json=json).json()
        self._update(response)
    
    def back(self):
        if self.step == 0:
            raise CantGoAnyFurther("error: unable to go back at the first question")
        url = f"{self.uri}/cancel_answer"
        json = {"sid": 1, "cm": str(self.child_mode).lower(), "step": self.step, "progression": self.progression, "session": self.session, "signature": self.signature}
        response = requests.post(url, json=json).json()
        self._update(response)

class ChoicesView(discord.ui.View):
    def __init__(self, timeout=180):
        self.value = None
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="はい", style=discord.ButtonStyle.blurple)
    async def button_y(self, interaction, button: discord.Button):
        self.value = 0
        await interaction.response.send_message("はい")
        self.stop()
    
    @discord.ui.button(label="いいえ", style=discord.ButtonStyle.blurple)
    async def button_n(self, interaction, button: discord.Button):
        self.value = 1
        await interaction.response.send_message("いいえ")
        self.stop()
    
    @discord.ui.button(label="わからない", style=discord.ButtonStyle.blurple)
    async def button_idk(self, interaction, button: discord.Button):
        self.value = 2
        await interaction.response.send_message("わからない")
        self.stop()
    
    @discord.ui.button(label="たぶんそう 部分的にそう", style=discord.ButtonStyle.blurple)
    async def button_p(self, interaction, button: discord.Button):
        self.value = 3
        await interaction.response.send_message("たぶんそう 部分的にそう")
        self.stop()
    
    @discord.ui.button(label="たぶん違う そうでもない", style=discord.ButtonStyle.blurple)
    async def button_pn(self, interaction, button: discord.Button):
        self.value = 4
        await interaction.response.send_message("たぶん違う そうでもない")
        self.stop()
    
    @discord.ui.button(label="修正する", style=discord.ButtonStyle.red)
    async def button_back(self, interaction, button: discord.Button):
        self.value = -1
        await interaction.response.send_message("修正する")
        self.stop()

class ConfirmationView(discord.ui.View):
    def __init__(self, timeout=180):
        self.value = None
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="はい", style=discord.ButtonStyle.green)
    async def button_y(self, interaction, button: discord.Button):
        self.value = 0
        await interaction.response.send_message("はい")
        self.stop()
    
    @discord.ui.button(label="いいえ", style=discord.ButtonStyle.red)
    async def button_n(self, interaction, button: discord.Button):
        self.value = 1
        await interaction.response.send_message("いいえ")
        self.stop()

def float_to_hex(x):
    return min(max(round(x*256), 0), 255)

def float_to_color(x):
    x = min(max(x, 0.0), 1.0)
    if x < 1/6:
        r, g, b = 1.0, x*6, 0.0
    elif x < 2/6:
        r, g, b = 1.0-(x-1/6)*6, 1.0, 0.0
    elif x < 3/6:
        r, g, b = 0.0, 1.0, (x-2/6)*6
    elif x < 4/6:
        r, g, b = 0.0, 1.0-(x-3/6)*6, 1.0
    elif x < 5/6:
        r, g, b = (x-4/6)*6, 0.0, 1.0
    else:
        r, g, b = 1.0, 0.0, 1.0-(x-5/6)*6
    return float_to_hex(r)*0x10000 + float_to_hex(g)*0x100 + float_to_hex(b)

async def play():
    minigame_channel = client.get_channel(MINIGAME_CHANNEL_ID)
    thread = await minigame_channel.create_thread(name="Akinator", type=discord.ChannelType.public_thread)
    aki = Akinator()
    miss_count = 0
    try:
        aki.start_game("jp")
        await thread.send("__**Akinator**__ 🧞\nやあ、私はアキネイターです\n有名な人物やキャラクターを思い浮かべて。魔人が誰でも当ててみせよう。魔人は何でもお見通しさ ✨")
        while True:
            while not aki.guessed:
                embed = discord.Embed(title="質問"+str(aki.step+1), color=float_to_color(aki.progression/100))
                embed.add_field(name=aki.question, value="下のモーダルから答えてね")
                embed.set_thumbnail(url=f"{aki.uri}/assets/img/akitudes_670x1096/{aki.akitude}")
                choices_view = ChoicesView()
                await thread.send(embed=embed, view=choices_view)
                await choices_view.wait()
                if choices_view.value is None:
                    await thread.send("3分間操作がなかったので終了するよ 👋")
                    return
                elif choices_view.value == -1:
                    if aki.step >= 1:
                        aki.back()
                    else:
                        await thread.send("これ以上前の問題には戻れないよ 💢")
                else:
                    aki.answer(choices_view.value)
            guess_embed = discord.Embed(title="思い浮かべているのは", color=float_to_color(aki.progression/100))
            guess_embed.add_field(name=aki.guess_name, value=aki.guess_description)
            guess_embed.set_image(url=aki.guess_image)
            confirmation_view = ConfirmationView()
            await thread.send(embed=guess_embed, view=confirmation_view)
            await confirmation_view.wait()
            if confirmation_view.value == 0:
                if miss_count == 0:
                    correct_message = "よぉし！また正解！！魔人は何でもお見通しだ 😤"
                elif miss_count == 1:
                    correct_message = "よぉし！正解したぞ ✌"
                elif miss_count == 2:
                    correct_message = "よかった！なんとか正解 😙"
                else:
                    correct_message = "ふぅ～、難しかったがようやく正解したようだ 😜"
                await thread.send(correct_message)
                channel_embed = discord.Embed(color=float_to_color(aki.progression/100))
                channel_embed.add_field(name=aki.guess_name, value=aki.guess_description)
                channel_embed.set_image(url=aki.guess_image)
                await minigame_channel.send(embed=channel_embed)
                return
            elif confirmation_view.value == 1:
                aki.exclude()
                miss_count += 1
            else:
                await thread.send("3分間操作がなかったので終了するよ ⌛")
                return
    except NoMoreQuestions:
        await thread.send("う～ん、魔人はそのキャラクターを知らないかも... 😵")
    except Exception as e:
        await thread.send(e)
        await thread.send("エラーが発生しました...やり直してね 😇")
        return