import discord
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

TOKEN = os.getenv("TOKEN")
BOT_NOTIFICATION_CHANNEL_ID = int(os.getenv("BOT_NOTIFICATION_CHANNEL_ID"))
MINIGAME_CHANNEL_ID = int(os.getenv("MINIGAME_CHANNEL_ID"))
CHAT_CHANNEL_ID = int(os.getenv("CHAT_CHANNEL_ID"))
