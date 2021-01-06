import discord
import youtube_dl
import random
import json
import asyncio
import shutil
import os
import datetime
import matplotlib
from discord.utils import get
from discord.ext import commands
from pytz import timezone

#Enter Bot token here
botToken = ""
#guid ID
_guildID = ""


prefix = "/"
client = commands.Bot(command_prefix=prefix)
client.remove_command('help')
joinROLE = "New Kid"
tz = timezone("EST")
#Enter Guild ID
guildT = client.get_guild(_guildID)
queues={}


@client.event
async def on_ready():
    print("=========-========")
    print("<[Bot]> Logged In.")
    print("=========-========")

@client.event
async def on_member_join(member):
    print("Member JOINED!")
    channel = get(member.guild.channels, name="welcome")
    pfp = member.avatar_url
    joinEmbed = discord.Embed(
        title = "Welcome!",
        description = f"{member.mention} to the best server!",
        colour = discord.Colour.blue()
    )
    joinEmbed.set_image(url=pfp)
    joinEmbed.timestamp = datetime.datetime.now(tz)
    joinEmbed.add_field(name="Rules", value="Read #rules before you ask questions!", inline=False)
    joinEmbed.add_field(name="Members", value=guildT.member_count, inline=False)
    role = get(member.guild.roles, name=joinROLE)


    # totalUsers = get(member.guild.channels, id=)
    # totalUsers.name(guildT.member_count)

    await member.add_roles(role)
    await channel.send(embed=joinEmbed)

@client.event
async def on_message(message):
    author = message.author.id
    print(message.content, author)
    await client.process_commands(message)


@client.command(pass_context=True, aliases=["j", "Join"])
async def join(ctx):
    print("Starting join function")
    global voice
    channel = ctx.message.author.voice.channel
    user = ctx.message.author

    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await ctx.send(f"I have has joined {channel}. and")

@client.command(pass_context=True, aliases=["l"])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    user = ctx.message.author

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"I have left {channel}.")

@client.command(pass_context=True, aliases=["stop", "s"])
async def pause(ctx):
    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("Music Paused...")
    else:
        await ctx.send("Failed to pause: Music not playing.")

@client.command(pass_context=True, aliases=["res", "start", "r"])
async def resume(ctx):
    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("Resuming Music...")
    else:
        await ctx.send("Resume Failed: Music not paused.")

@client.command(pass_context=True, aliases=["ski"])
async def skip(ctx):
    queues.clear()

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Music Skippied...")
    else:
        await ctx.send("Skipping... Failed: No music playing")

@client.command(pass_context=True, aliases=["q", "que?", "Q"])
async def queue(ctx, url:str):
    file = os.path.isdir("./Queue")
    if file is False:
        os.mkdir("Queue")
    dir = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(dir))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors':[{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio...")
        ydl.download([url])
        print("Download Finished.")
    await ctx.send("Queued: "+ str(q_num))

@client.command(pass_context=True, aliases=["pl", "p"])
async def play(ctx, url:str):

    def queue_checker():
        file = os.path.isdir("./Queue")
        if file is True:
            dir = os.path.abspath(os.path.abspath("Queue"))
            length = len(os.listdir(dir))
            in_q = length - 1
            try:
                first_File = os.listdir(dir)[0]
            except:
                print("No more queued songs... use /play <link> to play more songs")
                queues.clear()
                return
            main_loc = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.abspath("Queue") + "\\" + first_File)
            if length != 0:
                print("Playing next queued song...")
                print(f"Queue:\n{in_q}")
                song_left = os.path.isfile("song.mp3")
                if song_left:
                    os.remove("song.mp3")
                shutil.move(song_path, main_loc)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "song.mp3")

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: queue_checker())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.1
            else:
                queues.clear()
                return
        else:
            queues.clear()
            print("No queued songs")

    song_left = os.path.isfile("song.mp3")
    try:
        if song_left:
            os.remove("song.mp3")
            queues.clear()
            print("Old song files removed")
    except PermissionError:
        print("PermissionError: Song is being played.")
        await ctx.send("```PermissionError: Song is still playing.```")
        return

    file = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_folder is True:
            print("Removed old Queue folder.")
            shutil.rmtree(Queue_folder)
    except:
        print("No Old Queue Folder.")

    await ctx.send("Getting everything ready... please be patient.")

    print("Starting play function...")
    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors':[{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio...")
        ydl.download([url])
        print("Download Finished.")

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            os.rename(file, "song.mp3")

    print("Playing audio...")
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: queue_checker())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.1

    nname = name.rsplit("-", 2)

    pEmbed = discord.Embed()
    pEmbed.add_field(name="Now Playing...", value=url)

    await ctx.send(embed=pEmbed)

@client.command(aliases=["peepee","shlong"])
async def pp(ctx, member : discord.Member = None):
    size1 = random.randint(0,10)
    size = "=" * size1
    print(size)
    if member:
        author = member.display_name
    else:
        author = ctx.message.author.name
    if size1 <= 5:
        x = ["https://i.redd.it/9sx3tyfphwt11.jpg", "https://i.kym-cdn.com/photos/images/facebook/001/686/266/90a.jpg", "https://images7.memedroid.com/images/UPLOADED816/5e4b5529078c8.jpeg", "https://images3.memedroid.com/images/UPLOADED47/5d61547ae5a24.jpeg", "https://i.redd.it/62njhniyftg21.jpg", "https://i.redd.it/17nzj3sno9701.jpg"]
        urlPP = "https://www.urbandictionary.com/define.php?term=smol%20pp"
        urlP1 = random.choice(x)
    else:
        x = ["https://i.redd.it/vt59rlt4h9a41.png", "https://media.makeameme.org/created/i-got-big-4d46be717c.jpg", "https://images-na.ssl-images-amazon.com/images/I/41xsUggyswL._SR600%2C315_PIWhiteStrip%2CBottomLeft%2C0%2C35_SCLZZZZZZZ_.jpg", "https://i.redd.it/lhe5ovdfzxb41.png", "https://i.redd.it/fs0h43e940b41.jpg", "https://www.superiorsilkscreen.com/840/i-m-the-guy-with-the-huge-pp.jpg"]
        urlPP = "https://www.urbandictionary.com/define.php?term=Big%20Pp"
        urlP1 = random.choice(x)

    embedP=discord.Embed(
        title="",
        url=urlPP,
        description="8"+size+"D",
        color=0xe2bf74
     )
    embedP.set_author(name=author+" PP size")
    embedP.set_footer(text="This is 100% accurate.")
    embedP.add_field(name=author+" be like:", value="‎", inline=False)
    embedP.set_image(url=urlP1)

    await ctx.send(embed=embedP)

@client.command()
async def help(ctx):
    author = ctx.message.author

    chatEmbed = discord.Embed(
        Title = "ChatHelp",
        colour = discord.Colour.green()
    )

    chatEmbed.set_author(name="✔ Check Your DMs for help 😄")

    helpEmbed = discord.Embed(
        Title = "Help Menu",
        colour = discord.Colour.green()
    )

    helpEmbed.set_author(name="Bot Prefix: '/' ")
    helpEmbed.add_field(name="play", value="Plays music with a specific URL:\n /play <url>", inline=False)
    helpEmbed.add_field(name="pp", value="Measures your peepee size :wink:", inline=False)
    helpEmbed.add_field(name="queue", value="Adds a song to the queue with specific URL: \n /queue <url>", inline=False)
    helpEmbed.add_field(name="skip", value="Skips the current song", inline=False)
    helpEmbed.add_field(name="pause", value="Pauses the currently playing song", inline=False)
    helpEmbed.add_field(name="resume", value="Resumes a song that is paused", inline=False)
    #helpEmbed.add_field(name="", value="", inline=False)
    helpEmbed.set_footer(text="Made By: Pyro#3805")

    await ctx.send(embed=chatEmbed)
    await author.send(embed=helpEmbed)

client.run(botToken)
