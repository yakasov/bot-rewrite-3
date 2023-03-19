"""Generic commands for the bot."""

from configparser import ConfigParser
import os
from discord.ext import commands
import openai


class Commands(commands.Cog):
    """Class to hold all generic commands."""
    def __init__(self, bot):
        self.bot = bot
        self.c = ConfigParser()
        self.c.read(os.getcwd() + r"\resources\config.cfg")
        if self.c["features"].getboolean("openai_chat"):
            openai.api_key = self.c["features"]["openai_token"]


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


    @commands.command(name="ai", aliases=["ai2"])
    async def getairesponse2(self, ctx, *, content: str):
        """Uses OpenAI API (text-davinci-002) to generate an AI response."""
        if self.c["features"].getboolean("openai_chat") and \
            ctx.channel.name == "chat-with-output-bot":
            print(f"\nGenerating OpenAI reponse with prompt:\n{content}")
            await ctx.send(f"\nGenerating OpenAI reponse with prompt:\n{content}")
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=content,
                temperature=0.7,
                top_p=0.9,
                max_tokens=2048,
                stop=["<|endoftext|>"],
            )
            message = response.choices[0].text.strip()
            if len(message) > 2000:
                message = message[:2000]
            await ctx.reply(message)


    @commands.command(name="ai3", hidden=True)
    @commands.is_owner()
    async def getairesponse3(self, ctx, *, content: str):
        """Uses OpenAI API (text-davinci-003) to generate an AI response."""
        if self.c["features"].getboolean("openai_chat") and \
            ctx.channel.name == "chat-with-output-bot":
            print(f"\nGenerating OpenAI reponse with prompt:\n{content}")
            await ctx.send(f"\nGenerating OpenAI reponse with prompt:\n{content}")
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=content,
                temperature=0.7,
                top_p=0.9,
                max_tokens=1024,
                stop=["<|endoftext|>"],
            )
            message = response.choices[0].text.strip()
            if len(message) > 2000:
                message = message[:2000]
            await ctx.reply(message)


def setup(bot):
    """Add generic commands to bot."""
    bot.add_cog(Commands(bot))
