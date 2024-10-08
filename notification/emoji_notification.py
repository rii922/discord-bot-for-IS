import discord
from config import client, BOT_NOTIFICATION_CHANNEL_ID

async def emoji_notification(guild: discord.Guild, before: list[discord.Emoji], after: list[discord.Emoji]):
    if len(before) + 1 != len(after):
        return
    notification_channel: discord.TextChannel = client.get_channel(BOT_NOTIFICATION_CHANNEL_ID)
    s = set(before)
    for e in after:
        if not e in s:
            msg = await notification_channel.send(f"絵文字 {e} が追加されました！")
            await msg.add_reaction(e)
            return