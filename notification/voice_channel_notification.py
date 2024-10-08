import discord
from config import client, BOT_NOTIFICATION_CHANNEL_ID

async def voice_channel_notification(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel == after.channel:
        return
    notification_channel: discord.TextChannel = client.get_channel(BOT_NOTIFICATION_CHANNEL_ID)
    if isinstance(after.channel, discord.VoiceChannel) and before.channel is None:
        await notification_channel.send(f"<@{member.id}>が<#{after.channel.id}>に参加しました 🙌", delete_after=60)
        if len(after.channel.members) == 1:
            await notification_channel.send(f"通話<#{after.channel.id}>が開始しました 📢")
    elif isinstance(before.channel, discord.VoiceChannel) and after.channel is None:
        await notification_channel.send(f"<@{member.id}>が<#{before.channel.id}>から退出しました 👋", delete_after=60)
        if len(before.channel.members) == 0:
             await notification_channel.send(f"通話<#{before.channel.id}>が終了しました 📢")