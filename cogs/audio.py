"""Singing commands for the bot."""

from io import BytesIO
import asyncio
from discord import errors
from discord.ext import commands
from gtts import gTTS
from yt_dlp import YoutubeDL
import yt_dlp


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())


    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()


    @property
    def player(self):
        return self.current.player


    def skip(self):
        if self.is_playing():
            self.player.stop()


    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            self.current.player.start()
            await self.play_next_song.wait()


class Audio(commands.Cog):
    """Class to hold all audio commands."""
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_options = \
        {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}
        self.voice_states = {}


    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state
    

    async def create_voice_client(self, channel):
        voice = await channel.connect()
        state = self.get_voice_state(channel.server)
        state.voice = voice


    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass


    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel."""
        channel = ctx.message.author.voice.channel
        if channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.guild)
        if state.voice is None:
            try:
                state.voice = await channel.connect()
            except errors.ClientException:
                pass
        else:
            await state.voice.move_to(channel)

        return True


    @commands.command(name="play", aliases=["sing", "stream"])
    async def sing_yt(self, ctx, *, url: str):
        """Played audio from YouTube given URL."""
        state = self.get_voice_state(ctx.guild)
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

        if state.voice is None:
            success = await ctx.invoke(self.join)
            if not success:
                return

        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(url, download=False)
        url = info["url"]

        try:
            player = await state.voice.create_ytdl_player(url, ytdl_options=ydl_options)
        except (yt_dlp.utils.ExtractorError, yt_dlp.utils.DownloadError):
            await ctx.channel.send('URL not recognised.')
        except Exception as ex:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(ex).__name__, ex))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await state.songs.put(entry)


    @commands.command(name="tts", aliases=["talk"])
    async def tts(self, ctx, *, content: str):
        """Generate a TTS output from a given input."""
        state = self.get_voice_state(ctx.guild)

        if state.voice is None:
            success = await ctx.invoke(self.join)
            if not success:
                return

        tts = gTTS(text=content, lang='en')
        tts.save('tts.mp3')
        # mp3_fp = BytesIO()
        # tts.write_to_fp(mp3_fp)
        # mp3_fp.seek(0)


        try:
            player = await state.channel.create_ffmpeg_player('tts.mp3', options=self.ffmpeg_options)
        except Exception as ex:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await ctx.send(fmt.format(type(ex).__name__, ex))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await state.songs.put(entry)

        # async with ctx.typing():
        #     # ctx.voice_client.play(
        #     #     discord.FFmpegPCMAudio(source='tts.mp3', **self.ffmpeg_options))
        #     ctx.voice_client.play(await discord.FFmpegOpusAudio.from_probe('tts.mp3'))


    @commands.command(name="stop", aliases=["shutup"])
    async def stop_audio(self, ctx):
        """Stop playing audio."""
        state = self.get_voice_state(ctx.guild)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[ctx.guild.id]
            await state.voice.disconnect()
        except:
            pass


    @commands.command(name="leave", aliases=["leavevc", "disconnect", "dc"])
    async def leave_vc(self, ctx):
        """Leave current voice channel."""
        await ctx.voice_client.disconnect()


async def setup(bot):
    """Add audio commands to bot."""
    await bot.add_cog(Audio(bot))
