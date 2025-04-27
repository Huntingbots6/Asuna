# this module is created by HuntingBots on Github for AsunaRobot on Telegram

import json
import re
import html
from time import sleep
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, Chat, User, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_html
from AsunaRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from AsunaRobot.modules.log_channel import loggable
import AsunaRobot.modules.sql.chatbot_sql as sql
from AsunaRobot import openai_client

@user_admin_no_reply
@loggable
def chatbot_enable(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat

    sql.enable_openai(chat.id)  # Updated to use enable_openai
    query.answer()
    query.edit_message_text(
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"OpenAI Chatbot Enabled\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}",
        parse_mode=ParseMode.HTML,
    )
    return f"OpenAI Chatbot Enabled in {chat.title} by {user.first_name}"

@user_admin_no_reply
@loggable
def chatbot_disable(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat

    sql.disable_openai(chat.id)  # Updated to use disable_openai
    query.answer()
    query.edit_message_text(
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"OpenAI Chatbot Disabled\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}",
        parse_mode=ParseMode.HTML,
    )
    return f"OpenAI Chatbot Disabled in {chat.title} by {user.first_name}"

def chatbot_reply(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot

    if not sql.is_openai_enabled(chat_id):  # Updated to use is_openai_enabled
        return

    if message.text and not message.document:
        user_message = message.text
        bot.send_chat_action(chat_id, action="typing")

        try:
            # Use OpenAI API to get chatbot response
            completion = openai_client.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_message}]
            )
            ai_reply = completion.choices[0].message["content"]
            sleep(0.3)
            message.reply_text(ai_reply, timeout=60)
        except Exception as e:
            message.reply_text(f"Failed to get a response from OpenAI: {e}")

def chatbot_control_panel(update: Update, context: CallbackContext):
    user = update.effective_user
    chat = update.effective_chat
    keyboard = [
        [
            InlineKeyboardButton("Enable", callback_data=f"add_chat({chat.id})"),
            InlineKeyboardButton("Disable", callback_data=f"rm_chat({chat.id})"),
        ]
    ]
    update.effective_message.reply_text(
        f"Chatbot Control Panel for {html.escape(chat.title)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML,
    )

def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_openai_chats()  # Updated to use get_all_openai_chats
    text = "<b>OpenAI Chatbot Enabled Chats:</b>\n"
    for chat in chats:
        try:
            chat_obj = context.bot.get_chat(int(chat.chat_id))
            name = chat_obj.title or chat_obj.first_name
            text += f"• <code>{name}</code>\n"
        except Exception:
            sql.disable_openai(chat.chat_id)  # Cleanup broken entries

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

__help__ = """
*Admins only Commands*:
• `/chatbot` - Shows chatbot control panel
"""

__mod_name__ = "OpenAI ChatBot"

CHATBOT_CONTROL_HANDLER = CommandHandler("chatbot", chatbot_control_panel, run_async=True)
CHATBOT_ENABLE_HANDLER = CallbackQueryHandler(chatbot_enable, pattern=r"add_chat", run_async=True)
CHATBOT_DISABLE_HANDLER = CallbackQueryHandler(chatbot_disable, pattern=r"rm_chat", run_async=True)
CHATBOT_REPLY_HANDLER = MessageHandler(Filters.text & ~Filters.command, chatbot_reply, run_async=True)
LIST_ALL_CHATS_HANDLER = CommandHandler("allchats", list_all_chats, run_async=True)

dispatcher.add_handler(CHATBOT_CONTROL_HANDLER)
dispatcher.add_handler(CHATBOT_ENABLE_HANDLER)
dispatcher.add_handler(CHATBOT_DISABLE_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_REPLY_HANDLER)

__handlers__ = [
    CHATBOT_CONTROL_HANDLER,
    CHATBOT_ENABLE_HANDLER,
    CHATBOT_DISABLE_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_REPLY_HANDLER,
    ]
