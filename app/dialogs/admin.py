from decimal import Decimal
from sqlalchemy.orm import Session
from app import templ
from app import stuff
from app.models import Chat
from telegram import ParseMode, Bot, Update
from telegram.ext import CommandHandler
import logging
from cfg import BOT_TOKEN
from models import Donate
from models.donate import Currency


log = logging.getLogger(__name__)

@stuff.inject(chat=True)
@stuff.as_handler(CommandHandler, command='cancel', pass_chat_data=True)
def cancer(bot: Bot, update: Update, chat: Chat, chat_data: dict):
    """отменяет любые незавершённые диалоги"""
    chat_data.clear()
    bot.send_message(chat.id, 'ike..')


@stuff.as_handler(CommandHandler, command='admin', pass_chat_data=True, chat=True)
def go_admin(bot: Bot, update: Update, chat: Chat, chat_data: dict):
    if not chat.is_private:
        bot.send_message(chat.id, 'Давай в личку')
        return

    if chat.is_admin:
        bot.send_message(chat.id, 'Ты уже админ')
        return

    chat_data['go_admin_tries'] = chat_data.get('go_admin_tries', 0)
    bot.send_message(chat.id, 'Отправь мне мой нынешний токен чтобы стать админом')
    return 'проверить токен'


@stuff.inje
@stuff.dialog_part('проверить токен')
def verify_token(bot: Bot, update: Update, chat: Chat, chat_data: dict):
    chat_data['go_admin_tries'] += 1

    if chat_data['go_admin_tries'] == 3:
        bot.send_message(chat.id, 'Нет, так не пойдет')

    elif update.message.text.strip() == BOT_TOKEN:
        chat.is_admin = True
        bot.send_message(chat.id, 'Хорошо, теперь ты админ!')
        chat_data.pop('go_admin_tries')

    else:
        bot.send_message(chat.id, 'Это не тот токен')
        return 'проверить токен'


#
# Новый донат
#


@stuff.admin_only
@stuff.with_chat
@stuff.as_handler(CommandHandler, command='donate')
def new_donate(bot: Bot, update: Update, chat: Chat):
    bot.send_message(chat.id, 'какова сумма пожертвования?')
    return 'получить сумму пожертвования'


@stuff.with_chat
@stuff.dialog_part('получить сумму пожертвования')
def accept_new_donate_amount(bot: Bot, update: Update, chat: Chat, chat_data: dict):
    t = update.message.text

    try:
        amount, currency = t.strip().split()
    except Exception:
        amount, currency = t.strip(), None

    d = Donate(amount=Decimal(amount), currency= Currency[currency.upper()] if currency else None)  # KZT по умолчанию
    chat_data['new_donate'] = d
    bot.send_message(chat.id, 'Как зовут автора (или номер его телефона)?')

    return 'получить имя или телефон автора'


@stuff.with_chat
@stuff.with_session
@stuff.dialog_part('получить имя или телефон автора')
def accept_new_donate_author(bot: Bot, update: Update, sesh: Session, chat: Chat, chat_data: dict):

    t = update.message.text.strip()
    d = chat_data['new_donate']

    def save_donate():
        sesh.add(d)
        sesh.commit()
        bot.send_message(
            chat.id,
            f'Я сохранил донат, но о нём никто не узнает, '
            f'пока ты не разрешишь (/donates)',
            parse_mode=ParseMode.MARKDOWN
        )

    if t.lower() in ['не', 'нет', '-', 'no', 'nope', 'никак', 'ни как', 'отсутствует', 'жок', 'нит']:
        return save_donate()

    if t.startswith('8') or t.startswith('+7') or t.startswith('7'):
        d.author_phone = t
        if not d.author_name:
            bot.send_message(chat.id, 'А имя?')
    else:
        d.author_name = t
        if not d.author_phone:
            bot.send_message(chat.id, 'А телефон?')

    if not d.author_name or not d.author_phone:
        return 'получить имя или телефон автора'
    else:
        return save_donate()


@stuff.admin_only
@stuff.with_chat
@stuff.as_handler(CommandHandler, command='donates')
def view_donates(bot: Bot, update: Update, chat: Chat):
    dds = Donate.q.filter(Donate.counts == None).all()
    if dds:
        bot.send_message(
            chat.id,
            templ.get_template('uncounted-donates-list.md').render(dds=dds),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        bot.send_message(chat.id, 'Неподтверждённых донатов нет')
