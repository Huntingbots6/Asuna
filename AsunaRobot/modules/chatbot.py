import json
import re
import os
import html
import requests
from time import sleep
from telegram import ParseMode
from telegram import (CallbackQuery, Chat, MessageEntity, InlineKeyboardButton,
                      InlineKeyboardMarkup, Message, Update, Bot, User)
from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          DispatcherHandlerStop, Filters, MessageHandler)
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.utils.helpers import mention_html
from AsunaRobot.modules.helper_funcs.filters import CustomFilters
from AsunaRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from AsunaRobot import dispatcher, SUPPORT_CHAT
from AsunaRobot.modules.log_channel import loggable
import AsunaRobot.modules.sql.chatbot_sql as sql
from AsunaRobot import OpenAI


@user_admin_no_reply
@loggable
def chatbot_enable(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        chat: Optional[Chat] = update.effective_chat
        is_enabled = sql.set_kuki(chat.id)
        if is_enabled:
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI Enabled\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot already enabled by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )
    return ""

@user_admin_no_reply
@loggable
def chatbot_disable(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        chat: Optional[Chat] = update.effective_chat
        is_disabled = sql.rem_kuki(chat.id)
        if is_disabled:
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI Disabled\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot already disabled by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )
    return ""

@user_admin
@loggable
def chatbot_control_panel(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message
    msg = "Choose an option"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="Enable",
            callback_data="add_chat({})")],
       [
        InlineKeyboardButton(
            text="Disable",
            callback_data="rm_chat({})")]])
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

def chatbot_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() in ["ai", "chatbot"]:
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    return False

def chatbot_reply(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_enabled = sql.is_kuki(chat_id)
    if not is_enabled:
        return
    
    if message.text and not message.document:
        if not chatbot_message(context, message):
            return
        user_message = message.text
        bot.send_chat_action(chat_id, action="typing")
        
        # Use OpenAI API to get chatbot response
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": user_message}]
        )
        ai_reply = completion.choices[0].message["content"]
        sleep(0.3)
        message.reply_text(ai_reply, timeout=60)

def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_kuki_chats()
    text = "<b>OpenAI Chatbot-Enabled Chats</b>\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title or x.first_name
            text += f"• <code>{name}</code>\n"
        except (BadRequest, Unauthorized):
            sql.rem_kuki(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")

__help__ = """
*Admins only Commands*:
• `/chatbot`*:* Shows chatbot control panel
"""

__mod_name__ = "OpenAI ChatBot"

CHATBOT_CONTROL_HANDLER = CommandHandler("chatbot", chatbot_control_panel, run_async=True)
CHATBOT_ENABLE_HANDLER = CallbackQueryHandler(chatbot_enable, pattern=r"add_chat", run_async=True)
CHATBOT_DISABLE_HANDLER = CallbackQueryHandler(chatbot_disable, pattern=r"rm_chat", run_async=True)
CHATBOT_REPLY_HANDLER = MessageHandler(
    Filters.text & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!")
                    & ~Filters.regex(r"^\/")), chatbot_reply, run_async=True)
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats", list_all_chats, filters=CustomFilters.dev_filter, run_async=True)

dispatcher.add_handler(CHATBOT_ENABLE_HANDLER)
dispatcher.add_handler(CHATBOT_CONTROL_HANDLER)
dispatcher.add_handler(CHATBOT_DISABLE_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_REPLY_HANDLER)

__handlers__ = [
    CHATBOT_ENABLE_HANDLER,
    CHATBOT_CONTROL_HANDLER,
    CHATBOT_DISABLE_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_REPLY_HANDLER,
]
