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


    @commands.command(name="join", aliases=["joinvc", "summon", "connect"])
    async def join_author_vc(self, ctx):
        """Join voice channel of message author."""
        try:
            await ctx.author.voice.channel.connect()
        except AttributeError:
            await ctx.channel.send('Author not in a voice channel!')
        except discord.errors.ClientException:
            pass


    @commands.command(name="leave", aliases=["leavevc", "disconnect"])
    async def leave_vc(self, ctx):
        """Leave current voice channel."""
        try:
            await ctx.guild.voice_client.disconnect()
        except AttributeError:
            pass


    @commands.command(name="talk", aliases=["tts"])
    async def tts(self, ctx, *, content: str):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            channel_voice_stream = await channel.connect()

            tts = gTTS(text=content, lang='en')
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            channel_voice_stream.play(discord.FFmpegPCMAudio(mp3_fp))


    @commands.command(name="play", aliases=["sing", "stream"])
    async def sing_yt(self, ctx, *, url: str):
        """Played audio from YouTube given URL."""
        ydl_options = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'extractaudio': 'True',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '96',  # Highest bitrate Discord supports
            }],
        }
        ffmpeg_options = \
        {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}

        if ctx.author.voice:
            channel = ctx.author.voice.channel
            channel_voice_stream = await channel.connect()

        try:
            if not channel_voice_stream.is_playing():
                with YoutubeDL(ydl_options) as ydl:
                    info = ydl.extract_info(url, download=False)
                url = info["url"]
                channel_voice_stream.play(FFmpegOpusAudio(url, **ffmpeg_options))
                channel_voice_stream.is_playing()
        except (AttributeError, discord.errors.ClientException) as ex:
            print(ex)
            await ctx.channel.send('Make sure the bot is connected to a voice channel first!')
        except (yt_dlp.utils.ExtractorError, yt_dlp.utils.DownloadError):
            await ctx.channel.send('URL not recognised.')


    @commands.command(name="stop", aliases=["shutup"])
    async def stop_audio(self, ctx):
        """Stop playing audio."""
        channel_voice_stream = get(self.bot.voice_clients)
        try:
            channel_voice_stream.stop()
        except (discord.errors.ClientException, AttributeError):
            pass


def setup(bot):
    """Add audio commands to bot."""
    bot.add_cog(Audio(bot))
