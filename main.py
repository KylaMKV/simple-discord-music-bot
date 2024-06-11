TOKEN = "" # Insert your token here

PREFIX='_'

if TOKEN.strip() == "":
    print("Error: No token was given. Please read the README file in the github repo.")
    exit(1)
import os
import subprocess as sp
try:
    import discord
except:
    print("Error: Py-cord was not able to be imported, this means it is most likely not installed. Please install py-cord using 'pip'.")
    exit(0)

if os.system("which yt-dlp") != 0: # Check yt-dlp install
    print("Error: the yt-dlp command was not found in path. Please install yt-dlp.")
    exit(1)

intent = discord.Intents.default()
intent.message_content = True
client = discord.Client(intents=intent)

async def audio_player_thread(queuepos, msg):
    path = queuepos["filepath"]
    title = queuepos["title"]
    global vc
    if vc == None:
        return
    await vc.play(discord.FFmpegPCMAudio(path), wait_finish=True)
    if len(queue) > 0:
        await msg.channel.send(f"Finished '{title}', starting '{queue[1]['title']}' by '{queue[1]['artist']}' ")

        del queue[0]
        await audio_player_thread(queue[0], msg)


def get_info(search_term: str) -> tuple[str, str, str, str]|bool:
    data = None
    try:
        if search_term[:8] == "https://":
            data = sp.check_output(f"""yt-dlp --print "%(title)s\n%(channel)s\n%(original_url)s" --get-url "{search_term}" """, shell=True).decode()
        else:
            data = sp.check_output(f"""yt-dlp --print "%(title)s\n%(channel)s\n%(original_url)s" --get-url "ytsearch:{search_term}" """, shell=True).decode()
    except:
        return False
    data = data.split("\n")
    title = data[0]
    artist = data[1]
    url = data[2]
    streamurl = data[-2]
    return title, artist, url, streamurl

#Doing this cause the prebuilt embed constructor is weird
def construct_embed(title=None, artist=None, footer=None, url=None) -> discord.Embed:
    embed = discord.Embed(title=title, url=url)
    embed.set_footer(text=footer)
    embed.set_author(name=artist)
    return embed
async def edit_message(msg, msgdata: str|discord.Embed):
    if len(msg.embeds) == 0:
        await msg.edit(content=msgdata)
    if len(msg.embeds) > 0 and type(msgdata) == str:
        embed = msg.embeds[0]
        embed.set_footer(text=msgdata)
        await msg.edit(embed=embed)
    elif type(msgdata) == discord.Embed:
        msg.embeds.append(msgdata)
        await msg.edit(content="", embed=msgdata)


vc = None
# [ {title, artist, filepath} ]
queue = []
@client.event
async def on_ready():
    print("Bot online")
@client.event
async def on_message(msg):
    if msg.author == client.user or msg.content[0] != PREFIX:
        return
    global vc
    match msg.content.lower().split(" ")[0][1:]:
        case "play":
            search_term = " ".join(msg.content.split(" ")[1:])
            msgid = msg.id
            replymsg = await msg.reply("Searching...")

            returndata = get_info(search_term)
            if returndata == False: 
                print("Failed to download information.")
                await replymsg.edit(content="Failed to download information.")
                return

            # So my LSP doesn't give me 100+ errors:
            title, artist, url, streamurl = "", "", "", ""
            if type(returndata) == tuple: 
                title, artist, url, streamurl = returndata


            if len(title) > 256 or len(artist) > 256: # Embed title and artists has a max size of 256 characters
                new_msg_data = "Downloading '{title}' - '{artist}'"
            else:
                new_msg_data = construct_embed(title, artist, "Grabbing stream URL...", url)
            if not os.path.isdir("/tmp/musicbot"):
                os.mkdir("/tmp/musicbot/")
            await edit_message(replymsg, new_msg_data)


            queue.append({"filepath": streamurl, "title": title, "artist": artist})
            if vc != None and vc.is_playing() and len(queue) > 1:

                if type(new_msg_data) == str:
                    replymsg = await replymsg.edit(content=f"Downloaded! added to queue(Queue position: {len(queue)})")
                elif type(new_msg_data) == discord.Embed: # elif for LSP again
                    new_msg_data.set_footer(text=f"In queue (position as of now: {len(queue)})")
                    await replymsg.edit(embed=new_msg_data)

            elif len(queue) == 1:
                await edit_message(replymsg, "Playing!")
            vc = await msg.author.voice.channel.connect()
            await audio_player_thread(queue[0], msg)
        case "pause":
            if vc == None:
                await msg.reply("Not in a VC :(")
                return
            if vc.is_paused():
                await msg.reply("I'm already paused tho")
                return
            vc.pause()
        case "resume":
            if vc == None:
                await msg.reply("Not in a VC :(")
                return
            if vc.is_playing():
                await msg.reply("I'm already playing tho")
                return
            vc.resume()
        case "skip":
            if vc == None:
                await msg.reply("Im not in a VC :(")
                return
            vc.stop()
            await msg.reply(f"Skipping '{queue[0]['title']}', playing '{queue[1]['title']}'")
            del queue[0]
            await audio_player_thread(queue[0], msg)
        case "queue":
            replywith = ""
            index = 0
            for i in queue:
                replywith += f"{index+1}: {i['title']}\n"
                index += 1
            if replywith == "":
                replywith = "Queue is nonexistent."
            await msg.reply(replywith)
        case "leave":
            if vc == None:
                await msg.reply("Im not in a VC")
                return
            await msg.reply("ok :(")
            # LSP is giving me an error and I have no idea how to fix it
            # I hate async programming lol
            await vc.disconnect() 

            queue.clear()
        case "help":
            await msg.reply("""
_play {TITLE or URL}: downloads and plays a song/video in VC using youtube and yt-dlp.
_pause: Pauses the song currently being played.
_resume: Resumes the song previously paused.
_leave: Leaves the VC and clears queue.
_skip: Skips the song in the queue and removes it.
_queue: Lists the queue. queue also includes currently playing song/video.
""")



client.run(TOKEN)
