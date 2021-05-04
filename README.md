# Tony177-Pybot-Discord

Simple discord bot written in Python3 for educational purpose

# First Setup

- Install required modules in requirements.txt

```bash
pip3 install -r requirements.txt
```

- Customize config.txt (only token is <b>needed </b> to start)
- Add "Music" folder in main directory

# Working logic

Now the prefix is "!" without quotes. <br>
You can customize the bot as you prefer, modifing config.txt and global variable in the code. <br>

## Command

- <b><i>join </i></b> - works with the channel name (caps sensitive) and joins the voice channel
- <b><i>play </i></b> - works with the audio file name (without extension) and start playing an audio
- <b><i>yt </i></b> - works with the youtube link as first parameter, play the relative video as audio in the voice channel
- <b><i>dd </i></b> - works with the youtube link as first parameter, the name of the audio file as second parameter (without extension), will save it in the default Music directory (created before and changeble)
- <b><i>candd </i></b> - no needed parameters, change permission to use "dd" (can be used only by the role "Admin", can be easly changed)
- <b><i>volume </i></b> - works with the volume number (between 0 and 100) changing the default volume of the audio player
- <b><i>list </i></b> - no needed parameters, just print sorted list of audio in the default "list channel"
- <b><i>remove </i></b> - works with file name as first parameters, remove the audio from "Music" folder, the command is avaible only to "Admin" role and forbid the use of ".." and "/" keyword (remove remote possibility of exploring all drive)
- <b><i>stop </i></b> - no needed parameters, just stop and disconnects the bot from voice channel

# Thanks to

This program is avaible thanks to the following modules and API wrapper:

- Discord module
- Asyncio module
- Youtube_dl module
