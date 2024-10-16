import discord
from config import client, TOKEN, BOT_NOTIFICATION_CHANNEL_ID, MINIGAME_CHANNEL_ID
from keep_alive import keep_alive
from notification.voice_channel_notification import voice_channel_notification
from notification.emoji_notification import emoji_notification
from minigame.minigame import Minigame
from minigame.hangman import Hangman
from minigame.akinator import Akinator
from minigame.full_flash import FullFlash

minigames: list[Minigame] = [Hangman(), Akinator(), FullFlash()]

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
    command = message.content.strip().split()
    if command[0].lower() in ["help", "ヘルプ"]:
        help_msgs = [
            "`help` `ヘルプ`:\n"\
            "ヘルプを表示します 🔰\n"\
            "オプション引数として他のコマンドを与えると、そのコマンドに関する詳しいヘルプを表示します"
        ]
        if len(command) == 1:
            for minigame in minigames:
                help_msgs.append(f"{' '.join([f'`{minigame_command}`' for minigame_command in minigame.commands()])}:\n{minigame.help()}")
            await message.channel.send("\n\n".join(help_msgs))
            return
        else:
            for minigame in minigames:
                if command[1].lower() in minigame.commands():
                    await message.channel.send(minigame.help_detail())
                    return
    for minigame in minigames:
        if command[0].lower() in minigame.commands():
            await minigame.play(command[1:])
            break

keep_alive()
client.run(TOKEN)