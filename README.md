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

- <b><i>play </i></b> - command need just the audio file name (without extension)
- <b><i>dd </i></b> - command need as first parameter a youtube link and as second parameter the name of the audio file to be saved (without extension), it will be saved in Music directory (created before)

# Thanks to

This program is avaible thanks to the following modules and API wrapper:

- Discord module
- Asyncio module
- Youtube_dl module
