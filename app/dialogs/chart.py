from app import stuff
from app.models import Chat, Donate
from telegram import Bot, Update
from telegram.ext import CommandHandler
import logging

log = logging.getLogger(__name__)


@stuff.as_handler(CommandHandler, command='chart')
@stuff.inject(chat=True)
def get_chart(bot: Bot, update: Update, chat: Chat, sesh):
    pass
