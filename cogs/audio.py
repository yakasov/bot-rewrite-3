"""Singing commands for the bot."""

from io import BytesIO
import discord
from discord import FFmpegOpusAudio
from discord.ext import commands
from discord.utils import get
from gtts import gTTS
from yt_dlp import YoutubeDL
import yt_dlp


class Audio(commands.Cog):
    """Class to hold all audio commands."""
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_options = \
        {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}


    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel."""
        if ctx.author.voice:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.voice_client.move_to(ctx.author.voice.channel)


    @commands.command(name="play", aliases=["sing", "stream"])
    async def sing_yt(self, ctx, *, url: str):
        """Played audio from YouTube given URL."""
        ydl_options = {
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

        try:
            channel_voice_stream = get(self.bot.voice_clients, guild=ctx.guild)
            if not channel_voice_stream.is_playing():
                with YoutubeDL(ydl_options) as ydl:
                    info = ydl.extract_info(url, download=False)
                url = info["url"]
                channel_voice_stream.play(FFmpegOpusAudio(url, **self.ffmpeg_options))
                channel_voice_stream.is_playing()
        except (AttributeError, discord.errors.ClientException) as ex:
            await ctx.channel.send(ex)
        except (yt_dlp.utils.ExtractorError, yt_dlp.utils.DownloadError):
            await ctx.channel.send('URL not recognised.')


    @commands.command(name="tts", aliases=["talk"])
    async def tts(self, ctx, *, content: str):
        """Generate a TTS output from a given input."""
        if ctx.voice_client is None:
            await self.ensure_voice(ctx)

        tts = gTTS(text=content, lang='en')
        tts.save('tts.mp3')
        # mp3_fp = BytesIO()
        # tts.write_to_fp(mp3_fp)
        # mp3_fp.seek(0)

        async with ctx.typing():
            # ctx.voice_client.play(
            #     discord.FFmpegPCMAudio(source='tts.mp3', **self.ffmpeg_options))
            await ctx.channel.send(f"Pretty sure I'm in {ctx.voice_client.channel} right now...")
            ctx.voice_client.play(await discord.FFmpegOpusAudio.from_probe('tts.mp3'))


    async def ensure_voice(self, ctx):
        """Make sure bot is in voice chat before trying to use TTS or Sing!"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(reconnect=True)
            else:
                await ctx.channel.send("You are not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


    @commands.command(name="stop", aliases=["shutup"])
    async def stop_audio(self, ctx):
        """Stop playing audio."""
        channel_voice_stream = get(self.bot.voice_clients, guild=ctx.guild)
        if channel_voice_stream:
            channel_voice_stream.stop()


    @commands.command(name="leave", aliases=["leavevc", "disconnect", "dc"])
    async def leave_vc(self, ctx):
        """Leave current voice channel."""
        await ctx.voice_client.disconnect()


def setup(bot):
    """Add audio commands to bot."""
    bot.add_cog(Audio(bot))
