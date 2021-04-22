#!/usr/bin/env python3
import asyncio

import discord
import youtube_dl
import os

from discord.ext import commands

# Color costant
RED = "\033[1;31m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

# Config initialized to an empy dict
config = {}

# More info can be found on youtube-dl github repository
# Global stream options for ytdl
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

# Global download options for ytdl
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
    # Change working directory to this file's directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    with open("config.txt", "r") as file:
        f = file.readlines()
    if not f:
        raise FileNotFoundError("File doesn't exists or is corrupted")
    for line in f:
        # Removing blank space to filter empty line
        line = line.strip()
        # If startig with "#" is a comment
        if not line.startswith("#") and line:
            key = line.split("=")[0].strip()
            current_line = line.split("=")[-1].strip()
            config.update({key: current_line})
            # Every "boolean" strings return boolean
            if config[key] in ["true", "True", "False", "false"]:
                config.update({key: bool(current_line)})
    print(GREEN + "Loaded config file!" + RESET)


async def print_list():
    file_list = os.listdir("Music/")
    # Channel Object of "list" channel
    channel = bot.get_channel(768094168132091955)
    text = "There are " + str(len(file_list)) + " avaible audio track"
    await channel.purge(limit=2)  # Removing previous messagess
    file_list = sorted(file_list)
    for file in file_list:
        text += "\n|-> {}".format(file.split(".")[0] + " <-|")
    await channel.send(text)


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
    def __init__(self, bot_in):
        self.bot = bot_in

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
        """Streams from a url (doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print("Player error: %s" % e) if e else None
            )

        await ctx.send("Now playing: {}".format(player.title))

    @commands.command()
    async def candd(self, ctx):
        for role in ctx.author.roles:
            if str(role) == "Admin":
                config["can_download"] = not config["can_download"]
                await ctx.send("Now set can download: " + str(config["can_download"]))
                return
        await ctx.send("You don't have enought permission to use this command!")

    @commands.command()
    async def dd(self, ctx, *query):
        """Download a file into the local filesystem """
        if config["can_download"]:
            if not query:
                raise commands.CommandError("Syntax error in download command.")
            file_list = os.listdir("Music/")
            for f in file_list:
                if f.split(".")[0].lower() == str(query[1]).lower():
                    ctx.send("File alredy exists!")
                    raise commands.CommandError("File alredy exists!")

            download_format_options["outtmpl"] = "Music/{}.%(ext)s".format(
                str(query[1]).lower()
            )
            async with ctx.typing():
                download = youtube_dl.YoutubeDL(download_format_options)
                download.download([query[0]])
            await ctx.send(
                "Completed the download of: {}".format(str(query[1]).lower())
            )
            await print_list()
            print("The user {} downloaded the audio: {}").format(
                str(ctx.author), str(query[1])
            )
        else:
            await ctx.send("Download is disabled from config!")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def list(self, ctx):
        """Print the sorted list of audio file"""

        await print_list()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        if ctx.voice_client:
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
    await bot.change_presence(activity=discord.Game(name="@" + bot.user.name))
    print("Logged in as {0} ({0.id})".format(bot.user))
    print(GREEN + "Successfully started!" + RESET)
    print("------")


def main():
    start()
    bot.add_cog(Music(bot))
    bot.run(config["token"])


if __name__ == "__main__":
    main()
