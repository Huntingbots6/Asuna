# Module Credits: WilliamButcherBot & DaisyX
# Recode by @The_Ghost_Hunter On Telegram | @My_Asuna_Robot

import os
import aiofiles
import aiohttp
import asyncio
import time
import requests
import wget
from pyrogram import filters
from pyrogram.types import Message
from youtube_dl import YoutubeDL
from youtubesearchpython import SearchVideos
from tswift import Song
import lyricsgenius
from AsunaRobot import pbot as Asuna
from AsunaRobot.services.dark import get_arg
from AsunaRobot.services.setup import get_str_key
from AsunaRobot.utils.pluginhelper import get_text, progress

# Genius API Token
GENIUS = get_str_key("GENIUS_API_TOKEN", None)

# Saavn Music Handler
@Asuna.on_message(filters.command("saavn"))
async def saavn_music(client, message):
    args = get_arg(message) + " song"
    if not args.strip():
        await message.reply("<b>Enter a song name❗</b>")
        return

    m = await message.reply_text("Downloading your song, please wait ⏳️")
    try:
        response = requests.get(f"https://jostapi.herokuapp.com/saavn?query={args}")
        response.raise_for_status()
        data = response.json()[0]
        sname = data["song"]
        slink = data["media_url"]
        ssingers = data["singers"]

        file = wget.download(slink)
        ffile = file.replace("mp4", "m4a")
        os.rename(file, ffile)

        await message.reply_audio(audio=ffile, title=sname, performer=ssingers)
        os.remove(ffile)
    except Exception as e:
        await m.edit(f"Error: {e}")
    finally:
        await m.delete()

# Deezer Music Handler
async def fetch_deezer_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def download_deezer_song(url):
    song_name = "asuna.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(song_name, mode="wb") as f:
                    await f.write(await resp.read())
    return song_name

@Asuna.on_message(filters.command("deezer"))
async def deezer_music(_, message):
    if len(message.command) < 2:
        await message.reply_text("Provide a song name to download.")
        return

    query = message.text.split(None, 1)[1].replace(" ", "%20")
    m = await message.reply_text("Searching...")
    try:
        r = await fetch_deezer_data(f"https://thearq.tech/deezer?query={query}&count=1")
        title, url, artist = r[0]["title"], r[0]["url"], r[0]["artist"]

        await m.edit("Downloading...")
        song = await download_deezer_song(url)

        await message.reply_audio(audio=song, title=title, performer=artist)
        os.remove(song)
    except Exception as e:
        await m.edit(f"Error: {e}")
    finally:
        await m.delete()

# YouTube Video Handler
@Asuna.on_message(filters.command(["vsong", "video"]))
async def youtube_video(client, message: Message):
    query = get_text(message)
    if not query:
        await message.reply("Provide a song or video name.")
        return

    m = await client.send_message(message.chat.id, f"Searching for {query} on YouTube...")
    try:
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        result = search.result()["search_result"][0]
        video_url, title, channel, video_id = result["link"], result["title"], result["channel"], result["id"]
        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        file_name = f"{video_id}.mp4"
        opts = {
            "format": "best",
            "outtmpl": file_name,
            "quiet": True,
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        }

        with YoutubeDL(opts) as ytdl:
            ytdl.download([video_url])

        await client.send_video(message.chat.id, video=open(file_name, "rb"), caption=title, supports_streaming=True)
        os.remove(file_name)
    except Exception as e:
        await m.edit(f"Error: {e}")
    finally:
        await m.delete()

# YouTube Music Handler
@Asuna.on_message(filters.command(["music", "song"]))
async def youtube_music(client, message: Message):
    query = get_text(message)
    if not query:
        await message.reply("Provide a song name.")
        return

    m = await client.send_message(message.chat.id, f"Searching for {query} on YouTube...")
    try:
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        result = search.result()["search_result"][0]
        video_url, title, channel, video_id = result["link"], result["title"], result["channel"], result["id"]
        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        file_name = f"{video_id}.mp3"
        opts = {
            "format": "bestaudio",
            "outtmpl": file_name,
            "quiet": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        }

        with YoutubeDL(opts) as ytdl:
            ytdl.download([video_url])

        await client.send_audio(
            message.chat.id,
            audio=open(file_name, "rb"),
            title=title,
            performer=channel,
            thumb=thumbnail,
        )
        os.remove(file_name)
    except Exception as e:
        await m.edit(f"Error: {e}")
    finally:
        await m.delete()

# Lyrics Handlers
@Asuna.on_message(filters.command(["lyric", "lyrics"]))
async def lyrics_handler(client, message):
    query = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    if not query:
        await message.reply("Provide a song name.")
        return

    m = await message.reply("Searching for lyrics...")
    try:
        song = Song.find_song(query)
        if song and song.lyrics:
            await m.edit(song.format())
        else:
            await m.edit("Lyrics not found.")
    except Exception as e:
        await m.edit(f"Error: {e}")

@Asuna.on_message(filters.command(["glyric", "glyrics"]))
async def genius_lyrics(client, message):
    if "-" not in message.text:
        await message.reply("Use '-' to separate artist and song name. Example: /glyrics Artist - Song")
        return

    if GENIUS is None:
        await message.reply("Genius API token is not configured.")
        return

    args = message.text.split(None, 1)[1].split("-")
    artist, song = args[0].strip(), args[1].strip()

    m = await message.reply(f"Searching lyrics for {artist} - {song}...")
    try:
        genius = lyricsgenius.Genius(GENIUS)
        result = genius.search_song(song, artist)

        if result:
            await m.edit(f"Lyrics for {artist} - {song}:\n\n{result.lyrics}")
        else:
            await m.edit("Lyrics not found.")
    except Exception as e:
        await m.edit(f"Error: {e}")
