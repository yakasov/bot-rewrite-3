"""Generic commands for the bot."""

from configparser import ConfigParser
import os
import threading
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
Your name is 'outputbot', but your nickname is Angel (and you're a female bot)."},
        ]


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
    async def startai2thread(self, ctx, *, content: str):
        """Begins the normal AI thread."""
        threading.Thread(target=getairesponse2, args=(ctx, content)).start()

    async def getairesponse2(self, ctx, content: str):
        """Uses OpenAI API (text-davinci-002) to generate an AI response."""
        if self.c["features"].getboolean("openai_chat") and \
            ctx.channel.name == "chat-with-outputbot":
            print(f"\nGenerating OpenAI (text-davinci-002, 512 tokens) \
response with prompt:\n{content}")
            await ctx.send(
                f"\nGenerating OpenAI (text-davinci-002) response with prompt:\n{content}")
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=content,
                temperature=0.9,
                top_p=0.9,
                max_tokens=1024,
                stop=["<|endoftext|>"],
            )
            message = response.choices[0].text.strip()
            if len(message) > 2000:
                message = message[:2000]
            await ctx.reply(message)


    @commands.command(name="ai3", aliases=["aix"])
    async def startai3thread(self, ctx, *, content: str):
        """Begins the conversational AI thread."""
        threading.Thread(target=getairesponse3, args=(ctx, content)).start()

    async def getairesponse3(self, ctx, *, content: str):
        """Uses OpenAI API (gpt-3.5-turbo) to generate an AI response."""
        if self.c["features"].getboolean("openai_chat") and \
            ctx.channel.name == "chat-with-outputbot":
            print(f"\nGenerating OpenAI (gpt-3.5-turbo) \
response with prompt:\n{content}")
            await ctx.send(f"\nGenerating OpenAI (gpt-3.5-turbo) response with prompt:\n{content}")
            self.ai3messages.append({"role": "user", "content": content})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.ai3messages
            )
            message = response["choices"][0]["message"]
            self.ai3messages.append(message)
            if len(message["content"]) > 2000:
                message = message["content"][:2000]
            await ctx.reply(message["content"])


    @commands.command(name="refresh", hidden=True)
    @commands.is_owner()
    async def refreshmessages(self, ctx):
        """Refreshes the OpenAI AI3 messages."""
        self.ai3messages = [
            {"role": "system", "content":
             "You are a casual Discord chatting bot chatting in my personal Discord server.\
Your name is 'outputbot', but your nickname is Angel (and you're a female bot)."},
        ]
        await ctx.send("Removed all prior OpenAI messages.")


def setup(bot):
    """Add generic commands to bot."""
    bot.add_cog(Commands(bot))
