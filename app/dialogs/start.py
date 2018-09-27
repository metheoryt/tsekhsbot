from datetime import datetime, timedelta
from telegram import ParseMode
from telegram.ext import CommandHandler
import logging
from app import stuff
import time
from app import templ


log = logging.getLogger(__name__)


@stuff.as_handler(CommandHandler, command='start')
@stuff.inject(chat=True, sesh=True)
def shtart(bot, update, chat, sesh):
    """Приветствует новых пользователей или включает уведомления обратно"""

    if chat.muted:
        chat.muted = False
        bot.send_message(chat.id, '👌 ты в рассылке, мьют через /stop')  # OK emoji ((((:
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
