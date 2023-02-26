"""Generic commands for the bot."""

from discord.ext import commands

class Commands(commands.Cog):
    """Class to hold all generic commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, content: str):
        """Say something given a message."""
        await ctx.message.delete()
        await ctx.send(content)


    @commands.command()
    async def getpfp(self, ctx, *user_id):
        """Get profile picture of user given ID. If no ID, use author."""
        if user_id:
            try:
                await ctx.send(self.bot.get_user(int(user_id[0])).avatar_url)
            except (AttributeError, ValueError):
                await ctx.send("Invalid ID!")
        else:
            await ctx.send(ctx.author.avatar_url)


def setup(bot):
    """Add generic commands to bot."""
    bot.add_cog(Commands(bot))
