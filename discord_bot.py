import asyncio

import discord
import youtube_dl
import os

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

# Config initialized to an empy dict
config = {}

# More info can be found on youtube-dl github repository
## Global stream options for ytdl
stream_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

## Global download options for ytdl
download_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "Empty",
    "source_address": "0.0.0.0",
    "quiet": "true",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }
    ],
}

# Global converter options for ytdl
ffmpeg_options = {"options": "-vn"}


def start():
    with open("config.txt", "r") as file:
        f = file.readlines()
    if not f:
        raise FileNotFoundError("File doesn't exists or is corrupted")
    global config
    for line in f:
        # Removing blank space to filter empty line
        line = line.strip()
        # If startig with "#" is a comment
        if not line.startswith("#") and line:
            key = line.split("=")[0].strip()
            current_list = line.split("=")[-1].strip()
            config[key] = current_list
    print("Loaded config file!\n")


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        ytdl = youtube_dl.YoutubeDL(stream_format_options)
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("Music/" + query + ".mp3")
        )
        ctx.voice_client.play(
            source, after=lambda e: print("Player error: %s" % e) if e else None
        )

        await ctx.send("Now playing: {}".format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )

        await ctx.send("Now playing: {}".format(player.title))

    @commands.command()
    async def dd(self, ctx, *query):
        """Download a file into the local filesystem """

        if not query:
            ctx.send("Error: command value is empty!")
            return
        download_format_options["outtmpl"] = (
            "Music/" + str(query[1]).lower() + ".%(ext)s"
        )

        async with ctx.typing():
            download = youtube_dl.YoutubeDL(download_format_options)
            download.download([query[0]])
        await ctx.send("Complete download file: {}".format(str(query[1]).lower()))
        await print("The user " + ctx.author + " downloaded the audio " + str(query[0]))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Relatively simple music bot example",
)


@bot.event
async def on_ready():
    print("Logged in as {0} ({0.id})".format(bot.user))
    print("------")


def main():
    os.chdir(
        os.path.dirname(os.path.realpath(__file__))
    )  # Change working directory to this file's directory
    start()
    bot.add_cog(Music(bot))
    bot.run(config["token"])


if __name__ == "__main__":
    main()