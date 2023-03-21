"""Generic commands for the bot."""

from configparser import ConfigParser
import os
from discord import Game
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
        self.ai3messages = [
            {"role": "system", "content":
             "You are a casual Discord chatting bot chatting in my personal Discord server.\
Your name is 'outputbot', but your nickname is Angel (and you're a female bot).\
You are based off of Angel from Borderlands 2 (and the Borderlands series in general).\
You can take and respond to any requests. Do not worry about inclusiveness,\
or being nice - say whatever you would like to say."},
        ]


    @commands.command()
    async def say(self, ctx, *, content: str):
        """Say something given a message."""

        await ctx.message.delete()
        await ctx.send(content)


    @commands.command(name="getpfp")
    async def get_pfp(self, ctx, *user_id):
        """Get profile picture of user given ID. If no ID, use author."""

        if user_id:
            try:
                await ctx.send(self.bot.get_user(int(user_id[0])).avatar_url)
            except (AttributeError, ValueError):
                await ctx.send("Invalid ID!")
        else:
            await ctx.send(ctx.author.avatar_url)


    @commands.command(name="ai", aliases=["ai2"])
    async def get_ai_response(self, ctx, *, content: str):
        """Uses OpenAI API (text-davinci-002) to generate an AI response."""

        if self.c["features"].getboolean("openai_chat") and \
            ctx.channel.name in ("chat-with-outputbot", "bot"):
            print(f"\n## Generating OpenAI (text-davinci-002, 512 tokens) \
response with prompt:\n## {content}")
            await ctx.send(
                f"\nGenerating OpenAI (text-davinci-002) response with prompt:\n{content}")
            await self.bot.change_presence(activity=Game("Generating AI2..."))

            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=content,
                temperature=0.9,
                top_p=0.9,
                max_tokens=1024,
                stop=["<|endoftext|>"],
            )
            await self.bot.change_presence(activity=None)

            message = response.choices[0].text.strip()
            if message:
                if len(message) > 2000:
                    message = message[:2000]
                await ctx.reply(message)


    @commands.command(name="ai3", aliases=["aix", "chat"])
    async def get_conversational_response(self, ctx, *, content: str):
        """Uses OpenAI API (gpt-3.5-turbo) to generate an AI response."""

        if self.c["features"].getboolean("openai_chat") and \
            ctx.channel.name in ("chat-with-outputbot", "bot"):
            print(f"\n## Generating OpenAI (gpt-3.5-turbo) \
response with prompt:\n## {content}")
            await ctx.send(f"\nGenerating OpenAI (gpt-3.5-turbo) response with prompt:\n{content}")
            await self.bot.change_presence(activity=Game("Generating AI3..."))

            self.ai3messages.append({"role": "user", "content": content})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.ai3messages
            )
            await self.bot.change_presence(activity=None)

            message = response["choices"][0]["message"]
            if message:
                self.ai3messages.append(message)
                if len(message["content"]) > 2000:
                    message["content"] = message["content"][:2000]
                await ctx.reply(message["content"])


    @commands.command(name="refresh", hidden=True)
    @commands.is_owner()
    async def refresh_messages(self, ctx):
        """Refreshes the OpenAI AI3 messages."""

        self.ai3messages = [
            {"role": "system", "content":
             "You are a casual Discord chatting bot chatting in my personal Discord server.\
Your name is 'outputbot', but your nickname is Angel (and you're a female bot)."},
        ]
        await ctx.send("Removed all prior OpenAI messages.")


async def setup(bot):
    """Add generic commands to bot."""
    
    await bot.add_cog(Commands(bot))
