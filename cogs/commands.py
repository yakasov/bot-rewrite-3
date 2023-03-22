"""Generic commands for the bot."""

from configparser import ConfigParser
import os
from discord.ext import commands


class Commands(commands.Cog):
    """Class to hold all generic commands."""

    def __init__(self, bot):
        self.bot = bot
        self.c = ConfigParser()
        self.c.read(os.getcwd() + r"\resources\config.cfg")


    @commands.command()
    async def say(self, ctx, *, content: str =
                  commands.parameter(default="", description=": string to say")):
        """Say something given a message."""

        if not content:
            return None

        await ctx.message.delete()
        await ctx.send(content)


    @commands.command(name="getpfp")
    async def get_pfp(self, ctx, user_id: str =
                      commands.parameter(default=lambda ctx: ctx.author.avatar.url,
                                         description=": user ID to get the profile pic of")):
        """Get profile picture of user given ID. If no ID, use author."""

        if user_id:
            if user_id == ctx.author.avatar.url:
                return await ctx.send(user_id)
            try:
                await ctx.send(self.bot.get_user(int(user_id[0])).avatar.url)
            except (AttributeError, ValueError):
                await ctx.send("Invalid ID!")


async def setup(bot):
    """Add generic commands to bot."""

    await bot.add_cog(Commands(bot))
