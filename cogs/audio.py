"""Singing commands for the bot."""

import asyncio
from discord.ext import commands
from gtts import gTTS
from yt_dlp import YoutubeDL
import discord


ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}
ytdl_format_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extractaudio': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '96',  # Highest bitrate Discord supports
            }],
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
        }
ytdl = YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    """Class for YouTube audio stream."""
    def __init__(self, source, *, data, volume=0.8):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


    @classmethod
    async def from_url(cls, url, *, loop=None):
        """Get a YouTube audio stream from a given url."""

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Audio(commands.Cog):
    """Class to hold all audio related commands."""
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["summon"])
    async def join(self, ctx):
        """Joins a voice channel."""

        if not ctx.author.voice:
            return None
        channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()


    @commands.command(aliases=["sing", "play"])
    async def stream(self, ctx, *, url: str =
                     commands.parameter(default="",
                                        description=": the YouTube URL to stream audio from")):
        """Streams from a YouTube url."""

        if not url:
            return None

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player,
                                  after=lambda e: print(f'Player error: {e}') if e else None)


    @commands.command(aliases=["disconnect", "dc"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()


    @commands.command(aliases=["talk"])
    async def tts(self, ctx, *, content: str =
                  commands.parameter(default="",
                                     description=": content to pass to Google TTS service")):
        """Generate a TTS output from a given input."""

        if not content:
            return None

        tts = gTTS(text=content, lang='en')
        tts.save('tts.mp3')
        async with ctx.typing():
            player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('tts.mp3'))
            ctx.voice_client.play(player,
                                  after=lambda e: print(f'Player error: {e}') if e else None)


    @tts.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        """Ensure bot is in a voice channel before running a command."""

        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


async def setup(bot):
    """Add audio commands to bot."""

    await bot.add_cog(Audio(bot))
