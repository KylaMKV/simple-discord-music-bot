Just a simple music bot I made in like 2 hours using yt-dlp.

# Setup

prerequisites:
- A discord account(obviously)
- A linux-based system
- At least slight comfortability with the terminal
- [python](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [py-cord](https://docs.pycord.dev/en/stable/installing.html)

### 1. Create a new discord application
go to [Discords developer page](https://discord.com/developers) and click "New Application".

Type in a name you want the bot to be, click the checkbox and then "Create".

### 2. Generate the bot's Token and allow message reading

Click "Bot" at the right side of the screen, then "Reset Token", "Yes, do it!", If it prompts you to type in your password, please do so. After this, it will generate your discord bot's token. Copy this for later.

**DO NOT SHARE THIS WITH ANYONE**, this allow's the script to login as the bot. **ANYONE WITH THIS TOKEN CAN LOG IN TO YOUR BOT.**

While on this page, scroll down to where it says "Message Content Intent" and make sure that it is enabled. if it is not, enable it.

### 3. Download the script and add your token

Download the main.py file in the reposity either by downloading the reposity or [downloading the raw file from github](https://raw.githubusercontent.com/KylaMKV/simple-discord-music-bot/main/main.py)

Go to the line that says `TOKEN = ""`, (it should be the first one), add your token in the quotes(e.g `TOKEN="MTI1MDA3NjMyNzEz(...)"`)

### 4. Invite the bot to your server

go back to the developer page and click "Installation", make sure "Guild Install" is checked and "User Install" is not. Scroll down to Install Link, click the dropdown and click "Discord Provided URL." Scroll down and click the next dropdown and click "bot". in the Permissions dropdown find and click "Send Messages".

Click "Save Changes" and copy the URL under "Install Link". paste the URL in your browser in a new tab. Now click the drop down and choose the server you want to invite the bot to. **Keep in mind you must have at least Administrator access to the server in order to invite the bot.** Once you selected the server, click "Continue", and then Authorize. It should now be added to the server.

### 5. Run the script and enjoy!

Open a terminal, go to the path where the script is stored, and run `python3 main.py`
