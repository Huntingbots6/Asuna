import threading

from sqlalchemy import Column, String
from AsunaRobot.modules.sql import BASE, SESSION

class OpenAIChats(BASE):
    __tablename__ = "openai_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

OpenAIChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_openai_enabled(chat_id):
    """
    Check if OpenAI Chatbot is enabled for a specific chat.
    """
    try:
        chat = SESSION.query(OpenAIChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()

def enable_openai(chat_id):
    """
    Enable OpenAI Chatbot for a specific chat.
    """
    with INSERTION_LOCK:
        chat = SESSION.query(OpenAIChats).get(str(chat_id))
        if not chat:
            chat = OpenAIChats(str(chat_id))
        SESSION.add(chat)
        SESSION.commit()

def disable_openai(chat_id):
    """
    Disable OpenAI Chatbot for a specific chat.
    """
    with INSERTION_LOCK:
        chat = SESSION.query(OpenAIChats).get(str(chat_id))
        if chat:
            SESSION.delete(chat)
        SESSION.commit()

def get_all_openai_chats():
    """
    Retrieve all chats where OpenAI Chatbot is enabled.
    """
    try:
        return SESSION.query(OpenAIChats.chat_id).all()
    finally:
        SESSION.close()
