"""Generic commands for the bot."""

from discord.ext import commands
from init import bot as b


@commands.command()
async def say(ctx, *, content: str):
    """Say something given a message."""
    await ctx.message.delete()
    await ctx.send(content)


@commands.command()
async def getpfp(ctx, *user_id):
    """Get profile picture of user given ID. If no ID, use author."""
    if user_id:
        try:
            await ctx.send(b.get_user(int(user_id[0])).avatar_url)
        except (AttributeError, ValueError):
            await ctx.send("Invalid ID!")
    else:
        await ctx.send(ctx.author.avatar_url)


async def setup(bot):
    """Add admin commands to bot."""
    bot.add_command(say)
    bot.add_command(getpfp)
