"""
Yet another Discord bot rewrite.

Initial changes:
- components split up into different files, uses cogs to load commands
- birthdays as json for much easier reading
- config to avoid changing variables in py files
- requirements

Initial fixes:
- restart now awaits logout before logging back in, resulting in a much cleaner restart
- admin only commands now use is_owner() instead of hardcoded admin id
- queries now done in batches to avoid rate limiting

Author - yakasov
"""

from datetime import date
from time import gmtime, strftime
import os
import discord
from init import activity, bot, c
import tasks


def clear():
    """Clear console when called."""

    os.system("cls")


def get_name(ctx, thanks_type):
    """Get name in Thanks command."""

    msg = ctx.content.upper()
    result = ""
    if thanks_type in msg:
        result = msg[msg.find(thanks_type):].replace(thanks_type, "")

    if result.lower().strip() == "":
        return f" {str(ctx.author)[:-5]}"
    return f" *{result.lower().strip()}*"


async def react_to_message(ctx):
    """Add emojis to certain user messages."""

    emotes = {
        269143269336809483: "GnogChamp",  # Bojic
        899086657662365737: "mao",  # Xi Jinping
    }
    if ctx.author.id in emotes:
        emote = discord.utils.get(ctx.guild.emojis, name=emotes.get(ctx.author.id))
        if not emote:  # If not a custom emote, use string from dictionary
            emote = emotes.get(ctx.author.id)
        await ctx.add_reaction(emote)


@bot.event
async def on_ready():
    """Run when bot has connected to Discord successfully."""

    clear()
    await bot.change_presence(activity=activity)
    print(
        f'Connected and ready to go!\nCurrent date is {str(date.today().strftime("%d/%m"))},\
 logged in as {bot.user}'
    )

    tasks.check_current_date.start()
    if c["features"].getboolean("date_countdown"):
        tasks.set_nick_to_time.start()
    if c["features"].getboolean("minecraft_status"):
        tasks.query_mc_server.start()


@bot.listen("on_message")
async def on_message(message):
    """Run when a command has been sent in a channel the bot can see."""

    await react_to_message(message)
    if message.author.bot:
        return

    if message.content[0] == bot.command_prefix or message.author.id == 135410033524604928:
        print(
            f'\n{strftime("[%Y-%m-%d %H:%M:%S] ", gmtime())}\
    SERVER: {message.guild.name} | CHANNEL: {message.channel}\n{message.author}: {message.content}'
        )
        if message.attachments:
            for attached in message.attachments:
                print(f" > {attached.filename}")

    responses = {
        "LEAGUE": "league gay",
        "GOOD BOT": ":)",
        "BAD BOT": f"bad {str(message.author)[:-5]}",
        "DOG": "what da dog doin?\
        https://cdn.discordapp.com/attachments/542034119274790912/866427061718482944/\
unknown.png",
        "UEEIN NYOUGH":
        "https://cdn.discordapp.com/attachments/542034119274790912/1019249254335795240/\
YijBa5Jl4aKIkFP7.mp4",
    }

    t_list = ["THANKS", "TY", "THANK YOU", "THANK"]
    au_list = ["AMOG US", "AMOGUS", "SUS", "IMPOSTOR"]
    for t_type in t_list:
        responses[
            t_type
        ] = f"Thank you,{get_name(message, t_type)}\
, for your meaningful contribution!"
    for au_type in au_list:
        responses[au_type] = "https://tenor.com/view/19860632"

    for msg, res in responses.items():
        if f" {msg} " in f" {message.content.upper()} ":
            await message.channel.send(res)
            return  # Stop multiple replies in one message


bot.run(c["discord"]["token"])
