"""Initialise config and bot for all sub-files to use."""
from configparser import ConfigParser
import asyncio
import json
import os
import logging
from discord.ext import commands
import discord


def get_file(location):
    """Return contents of file at {location}."""
    if not os.path.exists(location):
        return None
    with open(location, "r", encoding="utf-8") as file:
        if location[-4:] == "json":
            result = json.load(file)
        else:
            result = file.read()
        file.close()
    return result


def write_file(location, content):
    """Write contents to file at {location}."""
    with open(location, "w", encoding="utf-8") as file:
        file.write(content)
        file.close()


c = ConfigParser()
c.read(os.getcwd() + r"\resources\config.cfg")

activity = discord.Activity(
    name=c["discord"]["activity"], type=discord.ActivityType.watching
)
allowed_mentions = discord.AllowedMentions(everyone=False, users=True)
help_category_fix = commands.DefaultHelpCommand(no_category="Commands")
intents = discord.Intents.all()
intents.members = True  # Subscribe to the privileged members intent
bot = commands.Bot(
    allowed_mentions=allowed_mentions,
    case_insensitive=True,
    command_prefix="*",
    help_command=help_category_fix,
    intents=intents,
)

extensions = ["cogs.admin", "cogs.ai", "cogs.audio", "cogs.commands"]
for extension in extensions:
    asyncio.run(bot.load_extension(extension))

logger = logging.getLogger("discord")
level = logging.getLevelName(c["discord"]["logger_level"])
logger.setLevel(c["discord"]["logger_level"])
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
discord.utils.setup_logging(level=level, root=False)

birthdays = get_file("resources/birthdays.json")
cache = get_file("resources/cache")
if not cache:
    write_file("resources/cache", "")
