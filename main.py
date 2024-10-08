import discord
from config import client, TOKEN, BOT_NOTIFICATION_CHANNEL_ID, MINIGAME_CHANNEL_ID
from keep_alive import keep_alive
from notification.voice_channel_notification import voice_channel_notification
from notification.emoji_notification import emoji_notification
from minigame import akinator

@client.event
async def on_ready():
    print("起動完了 💪")
    await client.get_channel(BOT_NOTIFICATION_CHANNEL_ID).send("起動完了 💪")

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    await voice_channel_notification(member, before, after)

@client.event
async def on_guild_emojis_update(guild: discord.Guild, before: list[discord.Emoji], after: list[discord.Emoji]):
    await emoji_notification(guild, before, after)

@client.event
async def on_message(message: discord.Message):
    if message.channel.id != MINIGAME_CHANNEL_ID:
        return
    if message.author.bot:
        return
    if message.content.strip() in akinator.COMMANDS:
        await akinator.play()

keep_alive()
client.run(TOKEN)