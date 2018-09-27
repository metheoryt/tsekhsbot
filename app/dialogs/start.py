from datetime import datetime, timedelta

from telegram import ParseMode
from telegram.ext import CommandHandler
import logging
from . import da_handler
import time
from app import templ


log = logging.getLogger(__name__)


@da_handler(CommandHandler, command='start')
def shtart(bot, update, sesh, chat):
    bot.send_message(chat.id, 'Привет!')

    if chat.created_at > datetime.utcnow() - timedelta(minutes=10):
        # хахахах
        time.sleep(1)
        bot.send_message(
            chat.id,
            templ.get_template('welcome.md').render(),
            parse_mode=ParseMode.MARKDOWN
        )
