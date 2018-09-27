from datetime import datetime, timedelta

from telegram import ParseMode
from telegram.ext import CommandHandler
import logging
from app import stuff
import time
from app import templ


log = logging.getLogger(__name__)


@stuff.with_chat
@stuff.with_session
@stuff.as_handler(CommandHandler, command='start')
def shtart(bot, update, sesh, chat):
    """Приветствует новых пользователей или включает уведомления обратно"""

    if chat.muted:
        chat.muted = False
        bot.send_message(chat.id, 'Ты в рассылке 👌, обратно - /заглохни👌')  # OK emoji ((((:
        return

    bot.send_message(chat.id, 'Привет!')

    if chat.created_at > datetime.utcnow() - timedelta(minutes=10):
        # хах
        time.sleep(1)
        bot.send_message(
            chat.id,
            templ.get_template('welcome.md').render(),
            parse_mode=ParseMode.MARKDOWN
        )
