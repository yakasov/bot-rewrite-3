"""Initialise config for all sub-files to use."""
from configparser import ConfigParser
import json
import os
import logging
from discord.ext import commands
import discord


def get_file(location):
    """Return contents of file at {location}."""
    with open(location, "r", encoding="utf-8") as file:
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
allowed_mentions = discord.AllowedMentions(users=True)
help_category_fix = commands.DefaultHelpCommand(no_category="Commands")
intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent
bot = commands.Bot(
    command_prefix="*",
    allowed_mentions=allowed_mentions,
    case_insensitive=True,
    help_command=help_category_fix,
    intents=intents,
)

logger = logging.getLogger("discord")
logger.setLevel(c["discord"]["logger_level"])
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

with open("resources/birthdays.json", "r", encoding="utf-8") as f:
    birthdays = json.load(f)
cache = get_file("resources/cache")
