"""Automated tasks for the bot."""

from datetime import date
from asyncio import sleep
from time import gmtime, mktime, strptime
from mcstatus import JavaServer
from discord import Game
from discord.ext import tasks
from init import birthdays, bot, c, cache, write_file


@tasks.loop(seconds=900)
async def check_current_date():
    """Check date every fifteen minutes,
    allowing for the bot to celebrate birthdays without a restart."""

    today = str(date.today().strftime("%d/%m"))
    if cache != today:
        guild = bot.get_guild(int(c["discord"]["guild"]))
        bday_channel = bot.get_channel(int(c["miscellaneous"]["bday_channel"]))
        bday_role = guild.get_role(int(c["miscellaneous"]["bday_role"]))

        await remove_birthday_role(guild, bday_role, today)
        await check_birthdays(guild, bday_channel, bday_role, today)
        write_file("resources/cache", today)


async def remove_birthday_role(guild, bday_role, today):
    """Remove birthday role from anybody that has it past their birthday."""

    for member in guild.members:
        try:
            if bday_role in member.roles and birthdays[str(member.id)]["date"] != today:
                await member.remove_roles(bday_role)
        except KeyError:
            pass


async def check_birthdays(guild, bday_channel, bday_role, today):
    """Check to see if it's someone's birthday! Uses birthday file from resources."""

    for member in guild.members:
        try:
            if birthdays[str(member.id)]["date"] == today:
                await bday_channel.send(
                    f"Happy Birthday, {birthdays[str(member.id)]['name']}! (<@{member.id}>)"
                )
                await member.add_roles(bday_role)
        except KeyError:
            pass


@tasks.loop(seconds=300)
async def set_nick_to_time():
    """Currently sets status to hours to Special Date!"""

    now = gmtime()
    special = strptime(c["miscellaneous"]["special_date"], '%d-%m-%y %H:%M:%S')
    hours = round((mktime(special) - mktime(now)) / 3600)
    await bot.change_presence(activity=Game(f"New Years in {hours} hours!"))


@tasks.loop(seconds=int(c["discord"]["presence_delay"]) * 2)
async def query_mc_server():
    """Rotate rich presence through functions below on certain delay."""

    server_1 = JavaServer(c["minecraft"]["server_1_ip"], int(c["minecraft"]["server_1_port"]))
    server_2 = JavaServer(c["minecraft"]["server_2_ip"], int(c["minecraft"]["server_2_port"]))
    await query_mc_server_players(server_1, server_2)
    await sleep(int(c["discord"]["presence_delay"]))
    await query_mc_server_names(server_1, server_2)


async def query_mc_server_players(server_1, server_2):
    """Query MCSERVER and set presence to amount of players online."""

    try:
        players_online = server_1.status().players.online + \
            server_2.status().players.online
        if players_online == 1:
            await bot.change_presence(activity=Game(
                f'Minecraft [{players_online} player]'))
        else:
            await bot.change_presence(activity=Game(
                f'Minecraft [{players_online} players]'))
    except (ConnectionRefusedError, ConnectionResetError, OSError):
        pass


async def query_mc_server_names(server_1, server_2):
    """Query MCSERVER and set presence to names of players online."""
    
    try:
        players = server_1.query().players.names + server_2.query().players.names
        player_display = '\n| '.join(players)
        if len(player_display) > 2:  # Don't update to empty status if nothing to show
            await bot.change_presence(activity=Game(player_display))
    except (ConnectionRefusedError, ConnectionResetError, OSError):
        pass
