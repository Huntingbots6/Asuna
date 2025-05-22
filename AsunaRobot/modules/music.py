"""
MIT License

Copyright (c) 2025 @HuntingBots for AsunaRobot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import aiohttp
import aiofiles
import requests
import tempfile
from mutagen import File as MutagenFile

from AsunaRobot.events import register as Asuna
from AsunaRobot import telethn as tbot

API_URL = "https://www.jiosaavn.com/api.php"

def saavn_search(query, limit=1):
    params = {
        "_format": "json",
        "__call": "search.getResults",
        "q": query,
        "p": 1,
        "n": limit,
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    resp = requests.get(API_URL, params=params, headers=headers)
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except Exception:
        text = resp.text
        json_start = text.find('{')
        import json as _json
        data = _json.loads(text[json_start:])
    results = data.get('results', [])
    if not results:
        return None
    return results[0]

async def download_file(url: str, file_name: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(file_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return file_name

async def download_image(url):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(temp.name, mode="wb") as f:
                    await f.write(await resp.read())
            else:
                temp.close()
                os.remove(temp.name)
                return None
    return temp.name

def set_metadata(filename, title, artist):
    try:
        audio = MutagenFile(filename, easy=True)
        if audio is not None:
            audio["title"] = title
            audio["artist"] = artist
            audio.save()
    except Exception:
        pass

@Asuna(pattern=r"^/saavn(?: |$)(.*)")
async def saavn_handler(event):
    args = event.pattern_match.group(1)
    if not args or args.strip() == "":
        await event.reply("<b>Enter song name❗</b>")
        return
    m = await event.reply("🔍 Searching JioSaavn ...")
    song = saavn_search(args)
    if not song:
        await m.edit("❌ Song not found on JioSaavn.")
        return
    title = song.get("title", "Unknown")
    artist = song.get("more_info", {}).get("singers") or song.get("artist") or "Unknown"
    image = song.get("image") or None

    # Duration must be an integer or None
    duration_str = song.get("more_info", {}).get("duration", "0")
    try:
        duration = int(float(duration_str))
        if duration <= 0:
            duration = 0
    except Exception:
        duration = 0

    # Get highest available quality
    media_url = None
    for k in ["320kbps", "160kbps", "96kbps"]:
        k_url = song.get("more_info", {}).get(f"encrypted_media_url_{k}", None)
        if k_url:
            media_url = k_url
            break
    if not media_url:
        media_url = song.get("more_info", {}).get("preview_url") or song.get("perma_url")
    if not media_url or not media_url.startswith("http"):
        await m.edit("❌ No downloadable audio found for this song.")
        return

    file_name = f"{title}.mp3"
    thumb_file = None
    if image and image.startswith("http"):
        try:
            thumb_file = await download_image(image)
            if not (thumb_file and os.path.exists(thumb_file)):
                thumb_file = None
        except Exception:
            thumb_file = None

    try:
        await m.edit("⬇️ Downloading audio ...")
        await download_file(media_url, file_name)
        set_metadata(file_name, title, artist)
    except Exception as e:
        if os.path.exists(file_name):
            os.remove(file_name)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)
        await m.edit(f"❌ Download failed: {e}")
        return

    try:
        await m.edit("📤 Uploading ...")
        from telethon.tl.types import DocumentAttributeAudio
        send_kwargs = {
            "file": file_name,
            "caption": f"{title}\n{artist}",
            "attributes": [
                DocumentAttributeAudio(
                    duration=duration,
                    performer=artist,
                    title=title,
                )
            ],
        }
        # Only pass thumb if it's a valid file
        if thumb_file and os.path.exists(thumb_file):
            send_kwargs["thumb"] = thumb_file
        await tbot.send_file(
            event.chat_id,
            **send_kwargs,
            reply_to=event.id,
        )
        os.remove(file_name)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)
        await m.delete()
    except Exception as e:
        await m.edit("❌ Upload failed: " + str(e))
        if os.path.exists(file_name):
            os.remove(file_name)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)
