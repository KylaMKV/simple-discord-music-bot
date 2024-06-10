TOKEN = "" # Insert your token here



import os
import subprocess as sp
import discord

intent = discord.Intents.default()
intent.message_content = True
client = discord.Client(intents=intent)

async def audio_player_thread(queuepos, msg):
    path = queuepos["filepath"]
    title = queuepos["title"]
    artist = queuepos["artist"]
    global vc
    if vc == None:
        return
    await vc.play(discord.FFmpegPCMAudio(path), wait_finish=True)
    if len(queue) > 0:
        await msg.channel.send(f"Finished '{title}', starting '{queue[1]['title']}' by '{queue[1]['artist']}' ")

        del queue[0]
        await audio_player_thread(queue[0], msg)


vc = None
# [ {title, artist, filepath} ]
queue = []
@client.event
async def on_ready():
    print("Bot online")
@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    global vc
    if msg.content.lower().startswith("_play"):
        search_term = " ".join(msg.content.split(" ")[1:])
        msgid = msg.id
        replymsg = await msg.reply("Searching...")
        if search_term[:8] == "https://":
            data = sp.check_output(f"""yt-dlp --print "%(title)s\n%(channel)s\n%(original_url)s" "ytsearch:{search_term}" """, shell=True).decode()
        else:
            data = sp.check_output(f"""yt-dlp --print "%(title)s\n%(channel)s\n%(original_url)s" "ytsearch:{search_term}" """, shell=True).decode()
        data = data.split("\n")
        title = data[0]
        artist = data[1]
        url = data[2]
        useEmbed = False
        if len(title) > 256 or len(artist) > 256:
            replymsg = await replymsg.edit(content=f"Downloading '{title}' by '{artist}'...")
        else:
            embed = discord.Embed(title=title, url=url)
            embed.set_footer(text="Downloading...")
            embed.set_author(name=artist)
            replymsg = await replymsg.edit(content="", embed=embed)
            useEmbed = True
        return_code = os.system(f""" yt-dlp -x --audio-format wav -o "/tmp/{msgid}.wav" "{url}" """)
        queue.append({"filepath": f"/tmp/{msgid}.wav", "title": title, "artist": artist})
        if vc != None and vc.is_playing() and len(queue) > 1:
            if not useEmbed:
                replymsg = await replymsg.edit(content=f"Downloaded! added to queue(Queue position: {len(queue)})")
            else:
                embed.set_footer(text=f"In queue (position as of now: {len(queue)})")
                await replymsg.edit(embed=embed)
        elif len(queue) == 1:
            if not useEmbed:
                replymsg = await replymsg.edit(content=f"Playing!")
            else:
                embed.set_footer(text="Playing!")
                await replymsg.edit(embed=embed)
        vc = await msg.author.voice.channel.connect()
        await audio_player_thread(queue[0], msg)
    elif msg.content.lower().startswith("_pause"):
        if vc == None:
            msg.reply("Not in a VC :(")
            return
        if vc.is_paused():
            await msg.reply("I'm already paused tho")
            return
        vc.pause()
    elif msg.content.lower().startswith("_resume"):
        if vc == None:
            msg.reply("Not in a VC :(")
            return
        if vc.is_playing():
            vc.reply("I'm already playing tho")
            return
        vc.resume()
    elif msg.content.lower().startswith("_skip"):
        if vc == None:
            await msg.reply("Im not in a VC :(")
            return
        vc.stop()
        await msg.reply(f"Skipping '{queue[0]['title']}', playing '{queue[1]['title']}'")
        del queue[0]
        await audio_player_thread(queue[0], msg)
    elif msg.content.lower().startswith("_queue"):
        replywith = ""
        index = 0
        for i in queue:
            replywith += f"{index+1}: {i['title']}\n"
            index += 1
        if replywith == "":
            replywith = "Queue is nonexistent."
        await msg.reply(replywith)
    elif msg.content.lower().startswith("_leave"):
        if vc == None:
            await msg.reply("Im not in a VC")
            return
        await msg.reply("ok :(")
        await vc.disconnect()
        queue.clear()
    elif msg.content.lower().startswith("_help"):
        await msg.reply("""
_play {TITLE or URL}: downloads and plays a song/video in VC using youtube and yt-dlp.
_pause: Pauses the song currently being played.
_resume: Resumes the song previously paused.
_leave: Leaves the VC and clears queue.
_skip: Skips the song in the queue and removes it.
_queue: Lists the queue. queue also includes currently playing song/video.
""")


client.run(TOKEN)
