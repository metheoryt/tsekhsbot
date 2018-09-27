from sqlalchemy.orm import Session
from app import stuff
from app.models import Chat
from telegram import Bot, Update
from telegram.ext import CommandHandler
import logging


log = logging.getLogger(__name__)


@stuff.as_handler(CommandHandler, command='/stop', pass_chat_data=True, allow_edited=True)
def mute(bot: Bot, update: Update, sesh: Session, chat: Chat, chat_data: dict):
    if not chat.muted:
        chat.muted = True
        bot.send_message(chat.id, '👌, вернуть обратно - /продолжай')  # OK emoji :))))
        return
