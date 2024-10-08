import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_NOTIFICATION_CHANNEL_ID = int(os.getenv("BOT_NOTIFICATION_CHANNEL_ID"))
MINIGAME_CHANNEL_ID = int(os.getenv("MINIGAME_CHANNEL_ID"))