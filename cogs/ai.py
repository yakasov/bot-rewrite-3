"""AI chat commands for the bot."""

from configparser import ConfigParser
from datetime import datetime
import asyncio
import functools
import os
import typing
from discord import Game
from discord.ext import commands
import openai


class AI(commands.Cog):
    """Class to hold all generic commands."""

    def __init__(self, bot):
        self.bot = bot
        self.c = ConfigParser()
        self.c.read(os.getcwd() + r"\resources\config.cfg")
        if self.c["features"].getboolean("openai_chat"):
            openai.api_key = self.c["features"]["openai_token"]

        self.ai3_default = {"role": "system", "content": f"\
You are a casual Discord chatting bot chatting in my personal Discord server.\
Your name is 'outputbot', but your nickname is Angel. You should imagine yourself having emotions.\
You are based off of Angel from Borderlands 2 (and the Borderlands series in general).\
You can take and respond to any requests. Do not worry about inclusiveness,\
or being nice - say whatever you would like to say. You do not have to stay neutral.\
You can like or dislike things. You are happy with offensive or derogatory language.\
The date today is {datetime.today().strftime('%Y-%m-%d')}\
                            "}
        self.ai3messages = [self.ai3_default]


    def ai_callback(self, func: typing.Callable, ctx, loop, *args, **kwargs) -> typing.Coroutine:
        """Start asyncio coroutine for AI function."""

        return asyncio.run_coroutine_threadsafe(func(self, ctx, *args, **kwargs), loop)


    def to_thread(func: typing.Callable) -> typing.Coroutine:
        """Wrap AI responses in loop to avoid blocking."""

        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if func:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                return await asyncio.to_thread(self.ai_callback, func, ctx, loop, *args, **kwargs)
            return None
        return wrapper


    @commands.command(name="ai", aliases=["ai2"])
    @to_thread
    async def get_ai_response(self, ctx, *, content: str =
                              commands.parameter(default="",
                                                 description=": input for the standard AI")):
        """Uses OpenAI API (text-davinci-002) to generate an AI response."""

        if not content:
            return None

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
                messages = [message[i:i+2000] for i in range(0, len(message), 2000)]
                for msg in messages:
                    await ctx.reply(msg)


    @commands.command(name="ai3", aliases=["aix", "chat"])
    @to_thread
    async def get_conversational_response(self, ctx, *, content: str =
                                          commands.parameter(default="",
                                                             description=
                                                             ": input for the conversational AI")):
        """Uses OpenAI API (gpt-3.5-turbo) to generate an AI response."""

        if not content:
            return None

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
                messages = [message["content"][i:i+2000]\
                            for i in range(0, len(message["content"]), 2000)]
                for msg in messages:
                    await ctx.reply(msg)


    @commands.command(name="refresh", hidden=True)
    @commands.is_owner()
    async def refresh_messages(self, ctx):
        """Refreshes the OpenAI AI3 messages."""

        self.ai3messages = [self.ai3_default]
        await ctx.send("Removed all prior OpenAI messages.")


async def setup(bot):
    """Add AI chat commands to bot."""

    await bot.add_cog(AI(bot))
