import asyncio
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest

from AsunaRobot import client  # Assuming client is the Telethon bot instance
from AsunaRobot.bot_plugins.permissions import can_change_info
from AsunaRobot.utils.errors import capture_err
from AsunaRobot.bot_plugins.dbfunctions import (
    alpha_to_int,
    get_karma,
    get_karmas,
    int_to_alpha,
    is_karma_on,
    karma_off,
    karma_on,
    update_karma,
)

regex_upvote = r"^((?i)\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍)$"
regex_downvote = r"^(\-|\-\-|\-1|👎)$"

OWNER_ID = 123456789  # Replace with the owner's ID


async def adjust_karma(event, increment=True):
    """Adjust karma for a user."""
    if not await is_karma_on(event.chat_id):
        return
    reply = await event.get_reply_message()
    if not reply or not reply.sender_id or not event.sender_id:
        return
    if reply.sender_id == OWNER_ID:
        owner_message = (
            "ᴡᴇʟʟ, ʜᴇ's ᴍʏ ᴏᴡɴᴇʀ. sᴏ ʏᴇᴀʜ, ʜᴇ ɪs ᴀʟᴡᴀʏs ʀɪɢʜᴛ ᴀɴᴅ ᴇᴠᴇʀʏᴏɴᴇ ᴋɴᴏᴡs ʜᴇ ɪs ᴀ ɢᴏᴏᴅ ᴘᴇʀsᴏɴ."
            if increment
            else "ᴡᴛғ ! ʏᴏᴜ ᴅᴏɴ'ᴛ ᴀɢʀᴇᴇ ᴡɪᴛʜ ᴍʏ ᴏᴡɴᴇʀ. ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀ ɢᴏᴏᴅ ᴩᴇʀsᴏɴ."
        )
        await event.reply(owner_message)
        return
    if reply.sender_id == event.sender_id:
        return
    chat_id = event.chat_id
    user_id = reply.sender_id
    user_mention = f"[{reply.sender.first_name}](tg://user?id={user_id})"
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    karma = current_karma["karma"] + 1 if increment else current_karma["karma"] - 1 if current_karma else 1 if increment else -1
    await update_karma(chat_id, await int_to_alpha(user_id), {"karma": karma})
    action = "ɪɴᴄʀᴇᴍᴇɴᴛᴇᴅ" if increment else "ᴅᴇᴄʀᴇᴍᴇɴᴛᴇᴅ"
    await event.reply(
        f"{action} ᴋᴀʀᴍᴀ ᴏғ {user_mention} ʙʏ 1.\n**ᴛᴏᴛᴀʟ ᴩᴏɪɴᴛs :** {karma}"
    )


async def fetch_karma_stats(event):
    """Fetch and display karma statistics."""
    chat_id = event.chat_id
    m = await event.reply("Analyzing Karma...Will Take 10 Seconds")
    karma = await get_karmas(chat_id)
    if not karma:
        await m.edit("No karma in DB for this chat.")
        return
    msg = f"**Karma list of {event.chat.title}:- **\n"
    limit = 0
    karma_dicc = {}
    for i in karma:
        user_id = await alpha_to_int(i)
        user_karma = karma[i]["karma"]
        karma_dicc[str(user_id)] = user_karma
    karma_arranged = dict(
        sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True)
    )
    if not karma_dicc:
        await m.edit("No karma in DB for this chat.")
        return
    for user_idd, karma_count in karma_arranged.items():
        if limit > 9:
            break
        try:
            user = await client(GetFullUserRequest(int(user_idd)))
            await asyncio.sleep(0.8)
        except Exception:
            continue
        first_name = user.user.first_name
        if not first_name:
            continue
        username = user.user.username
        msg += f"**{karma_count}**  {(first_name[0:12] + '...') if len(first_name) > 12 else first_name}  `{('@' + username) if username else user_idd}`\n"
        limit += 1
    await m.edit(msg)


# Upvote Event
@client.on(
    events.NewMessage(
        pattern=regex_upvote,
        func=lambda e: e.is_group and e.is_reply and not e.via_bot and not e.outgoing,
        incoming=True,
    )
)
@capture_err
async def upvote(event):
    await adjust_karma(event, increment=True)


# Downvote Event
@client.on(
    events.NewMessage(
        pattern=regex_downvote,
        func=lambda e: e.is_group and e.is_reply and not e.via_bot and not e.outgoing,
        incoming=True,
    )
)
@capture_err
async def downvote(event):
    await adjust_karma(event, increment=False)


# Karma Statistics
@client.on(events.NewMessage(pattern="/karmastat", func=lambda e: e.is_group))
@capture_err
async def karma(event):
    await fetch_karma_stats(event)


# Toggle Karma System
@client.on(events.NewMessage(pattern="/karma"))
@can_change_info
async def captcha_state(event):
    usage = "**Usage:**\n/karma [ON|OFF]"
    if len(event.text.split()) != 2:
        return await event.reply(usage)
    state = event.text.split(None, 1)[1].strip().lower()
    if state == "on":
        await karma_on(event.chat_id)
        await event.reply("Enabled karma system.")
    elif state == "off":
        await karma_off(event.chat_id)
        await event.reply("Disabled karma system.")
    else:
        await event.reply(usage)
