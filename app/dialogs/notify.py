from sqlalchemy.orm import Session
from app.dialogs import da_handler
from app.models import Chat
from telegram import Bot, Update
from telegram.ext import CommandHandler
import logging


log = logging.getLogger(__name__)


@da_handler(CommandHandler, command='заглохни', pass_chat_data=True, allow_edited=True)
def mute(bot: Bot, update: Update, sesh: Session, chat: Chat, chat_data: dict):
    if not chat.muted:
        chat.muted = True
        bot.send_message(chat.id, '👌, вернуть обратно - /продолжай')  # OK emoji :))))
        return


@da_handler(CommandHandler, command='продолжай', pass_chat_data=True, allow_edited=True)
def unmute(bot: Bot, update: Update, sesh: Session, chat: Chat, chat_data: dict):
    if chat.muted:
        chat.muted = False
        bot.send_message(chat.id, 'Ты в рассылке 👌, обратно - /заглохни👌')  # OK emoji ((((:
