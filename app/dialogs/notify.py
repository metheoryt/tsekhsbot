from app import stuff
from app.models import Chat
from telegram import Bot, Update
from telegram.ext import CommandHandler
import logging


log = logging.getLogger(__name__)


@stuff.as_handler(CommandHandler, command='stop', chat=True)
def mute(bot: Bot, update: Update, chat: Chat):
    if not chat.muted:
        chat.muted = True
        bot.send_message(chat.id, '👌, вернуть обратно - /start')  # OK emoji :))))
        return
