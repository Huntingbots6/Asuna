"""
MIT License

Copyright (c) 2025 HuntingBots

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

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, MessageHandler, Filters
from AsunaRobot import GROQ_API_KEY, dispatcher, LOGGER
from AsunaRobot.modules.sql.chatbot_sql import is_openai_enabled, enable_openai, disable_openai, get_all_openai_chats
from AsunaRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply 

__mod_name__ = "ChatBot"
__help__ = """
Admins Only:
• /chatbot - Open chatbot control panel
• /addchat - Enable chatbot in the current chat
• /rmchat - Disable chatbot in the current chat
"""

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROQ_API_KEY}",
}

# Enable chatbot for a specific chat
@user_admin
def enable_chatbot(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if is_openai_enabled(chat_id):
        update.message.reply_text("ChatBot is already enabled in this chat.")
        return
    enable_openai(chat_id)
    update.message.reply_text("ChatBot has been enabled in this chat!")

# Disable chatbot for a specific chat
@user_admin
def disable_chatbot(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not is_openai_enabled(chat_id):
        update.message.reply_text("ChatBot is already disabled in this chat.")
        return
    disable_openai(chat_id)
    update.message.reply_text("ChatBot has been disabled in this chat!")

# Chatbot control panel
@user_admin
def chatbot_panel(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    keyboard = [
        [InlineKeyboardButton("Enable", callback_data=f"enable_chat({chat_id})"),
         InlineKeyboardButton("Disable", callback_data=f"disable_chat({chat_id})")],
    ]
    update.message.reply_text(
        "ChatBot Control Panel:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# Handle callback queries for the control panel
@user_admin_no_reply
def chatbot_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = update.effective_chat.id

    if "enable_chat" in query.data:
        enable_openai(chat_id)
        query.answer("ChatBot enabled!")
        query.edit_message_text("ChatBot has been enabled in this chat.")
    elif "disable_chat" in query.data:
        disable_openai(chat_id)
        query.answer("ChatBot disabled!")
        query.edit_message_text("ChatBot has been disabled in this chat.")
    else:
        query.answer("Invalid action.")

# Respond to user messages when ChatBot is enabled
def chatbot_reply(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not is_openai_enabled(chat_id):
        return

    user_message = update.message.text
    if not user_message:
        return

    try:
        # Use Groq API to generate a response
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": user_message}],
        }
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        data = response.json()

        # Extract the bot's reply
        bot_reply = data.get("choices", [])[0].get("message", {}).get("content", "I couldn't generate a response.")
        update.message.reply_text(bot_reply)
    except Exception as e:
        LOGGER.error(f"Error in ChatBot reply: {e}")
        update.message.reply_text("Failed to generate a response. Please try again later.")

# List all chats with ChatBot enabled
@user_admin
def list_chats(update: Update, context: CallbackContext):
    chats = get_all_openai_chats()
    if not chats:
        update.message.reply_text("No chats have ChatBot enabled.")
        return

    text = "Chats with ChatBot enabled:\n"
    for chat in chats:
        text += f"• {chat.chat_id}\n"

    update.message.reply_text(text)

# Handlers
CHATBOT_ENABLE_HANDLER = CommandHandler("addchat", enable_chatbot, run_async=True)
CHATBOT_DISABLE_HANDLER = CommandHandler("rmchat", disable_chatbot, run_async=True)
CHATBOT_PANEL_HANDLER = CommandHandler("chatbot", chatbot_panel, run_async=True)
CHATBOT_REPLY_HANDLER = MessageHandler(Filters.text & ~Filters.command, chatbot_reply, run_async=True)
CHATBOT_CALLBACK_HANDLER = CallbackQueryHandler(chatbot_callback, pattern=r"enable_chat|disable_chat", run_async=True)
CHATBOT_LIST_HANDLER = CommandHandler("listchats", list_chats, run_async=True)

# Add handlers to dispatcher
dispatcher.add_handler(CHATBOT_ENABLE_HANDLER)
dispatcher.add_handler(CHATBOT_DISABLE_HANDLER)
dispatcher.add_handler(CHATBOT_PANEL_HANDLER)
dispatcher.add_handler(CHATBOT_REPLY_HANDLER)
dispatcher.add_handler(CHATBOT_CALLBACK_HANDLER)
dispatcher.add_handler(CHATBOT_LIST_HANDLER)
