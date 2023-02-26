"""Admin commands for the bot."""

from subprocess import Popen
from discord.ext import commands
import discord
from init import bot as b, c


@commands.command()
async def restart(ctx):
    """Restart bot. (Admin only)"""
    if ctx.author.id == c["discord"]["admin_id"]:
        await b.change_presence(activity=discord.Game("Restarting..."))
        with Popen("python bot.py"):
            raise SystemExit


@commands.command()
async def stop(ctx):
    """Stop bot. (Admin only)"""
    if ctx.author.id == c["discord"]["admin_id"]:
        raise SystemExit


@commands.command()
async def getallpfps(ctx):
    """Sends all profile pictures for everyone in server. (Admin only)"""
    if ctx.author.id == c["discord"]["admin_id"]:
        for user in ctx.guild.members:
            await ctx.send(f"{user.name}\n{user.avatar_url}")


@commands.command()
async def setpfp(ctx, *rel_path):
    """Set bot profile picture using relative path. (Admin only)"""
    if ctx.author.id == c["discord"]["admin_id"]:
        try:
            with open(rel_path[0], "rb") as avatar:
                await b.user.edit(avatar=avatar.read())
                await ctx.send("Avatar successfully changed!")
        except (FileNotFoundError, TypeError):
            await ctx.send(f"avatar.png not found! @ /{rel_path[0]}")
        except discord.errors.HTTPException:
            await ctx.send(
                "You are changing your avatar too fast. Please try again later."
            )


async def setup(bot):
    """Add admin commands to bot."""
    bot.add_command(restart)
    bot.add_command(stop)
    bot.add_command(getallpfps)
    bot.add_command(setpfp)
