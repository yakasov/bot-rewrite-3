"""Admin commands for the bot."""

from subprocess import Popen
from discord.ext import commands
import discord


class Admin(commands.Cog):
    """Class to hold all admin commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, _ctx):
        """Reload bot."""

        await self.bot.change_presence(activity=discord.Game("Restarting..."))
        Popen("python main.py")
        await self.bot.close()


    @commands.command(name="stop_bot", aliases=["stopbot", "kill", "logout"], hidden=True)
    @commands.is_owner()
    async def stop(self, _ctx):
        """Stop bot."""

        await self.bot.close()


    @commands.command(name="getallpfps", hidden=True)
    @commands.is_owner()
    async def get_all_pfps(self, ctx):
        """Sends all profile pictures for everyone in server."""

        for user in ctx.guild.members:
            await ctx.send(f"{user.name}\n{user.avatar.url}")


    @commands.command(name="setpfp", hidden=True)
    @commands.is_owner()
    async def set_pfp(self, ctx, rel_path: str =
                      commands.parameter(default="", description=": local path to img")):
        """Set bot profile picture using relative path.)"""

        if not rel_path:
            return None

        try:
            with open(rel_path[0], "rb") as avatar:
                await self.bot.user.edit(avatar=avatar.read())
                await ctx.send("Avatar successfully changed!")
        except IndexError:
            pass
        except (FileNotFoundError, TypeError):
            await ctx.send(f"avatar.png not found! @ /{rel_path[0]}")
        except discord.errors.HTTPException:
            await ctx.send(
                "You are changing your avatar too fast. Please try again later."
            )


async def setup(bot):
    """Add admin commands to bot."""

    await bot.add_cog(Admin(bot))
