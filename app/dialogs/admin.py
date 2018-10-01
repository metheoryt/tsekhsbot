import re
from decimal import Decimal
from sqlalchemy.orm import Session
import sqlalchemy as sa
from app import templ
from app import stuff
from app.models import Chat
from telegram import ParseMode, Bot, Update
from telegram.ext import CommandHandler, RegexHandler
import logging

from app.models.misc import DonateAuthor
from cfg import BOT_TOKEN
from app.models import Donate


log = logging.getLogger(__name__)


@stuff.as_handler(CommandHandler, command='cancel', pass_chat_data=True)
@stuff.inject(chat=True)
def cancer(bot: Bot, update: Update, chat: Chat, chat_data: dict):
    """отменяет любые незавершённые диалоги"""
    chat_data.clear()
    bot.send_message(chat.id, 'ike..')


@stuff.as_handler(CommandHandler, command='admin', pass_chat_data=True)
@stuff.inject(chat=True)
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


@stuff.dialog_part('проверить токен')
@stuff.inject(chat=True, sesh=True)  # sesh коммитит изменения если всё хорошо
def verify_token(bot: Bot, update: Update, chat: Chat, sesh, chat_data: dict):
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

@stuff.as_handler(CommandHandler, command='donate')
@stuff.admin_only
@stuff.inject(chat=True)
def new_donate(bot: Bot, update: Update, chat: Chat):
    bot.send_message(chat.id, 'какова сумма пожертвования?')
    return 'получить сумму пожертвования'


@stuff.dialog_part('получить сумму пожертвования')
@stuff.inject(chat=True)
def accept_new_donate_amount(bot: Bot, update: Update, chat: Chat, chat_data: dict):
    t = update.message.text

    try:
        amount, currency = t.strip().split()
    except Exception:
        amount, currency = t.strip(), None

    # currency KZT по умолчанию
    d = Donate(amount=Decimal(amount), currency=Donate.Currency[currency.upper()] if currency else None)
    chat_data['new_donate'] = d
    bot.send_message(chat.id, 'Как зовут автора? Можно часть имени, и если он уже есть, я предложу варианты.'
                              'Если не найду - сохраню как нового.')

    return 'получить имя автора'


@stuff.dialog_part('получить имя автора')
@stuff.inject(chat=True, sesh=True)
def accept_new_donate_author(bot: Bot, update: Update, chat: Chat, sesh: Session, chat_data: dict):

    t = update.message.text.strip()
    d = chat_data['new_donate']

    authors = DonateAuthor.q.filter(DonateAuthor.name.ilike(f'%{t.lower()[1:-1]}%')).all()

    if authors:
        msg = 'Один из них? Отправь его ID\n'
        for a in authors:
            msg += f'{a.id} - {a.name}'
            if a.phone:
                msg += f'({a.phone})'
            msg += '\n'
        bot.send_message(chat.id, msg)
        return 'получить ID автора'

    else:
        assert len(t > 4)
        na = DonateAuthor(name=t.title())
        sesh.add(na)
        d.author = na

    return 'сохранить донат'


@stuff.dialog_part('получить ID автора')
@stuff.inject(chat=True, sesh=True)
def accept_author_id(bot: Bot, update: Update, chat: Chat, sesh: Session, chat_data: dict):
    d = chat_data['new_donate']
    aid = int(update.message.text.strip())
    a = DonateAuthor.q.get(aid)
    assert a is not None
    d.author = a
    return 'сохранить донат'


@stuff.dialog_part('сохранить донат')
@stuff.inject(chat=True, sesh=True)
def save_new_donate(bot: Bot, update: Update, chat: Chat, sesh: Session, chat_data: dict):
    d = chat_data['new_donate']
    sesh.add(d)
    bot.send_message(
        chat.id,
        f'Я сохранил донат, но о нём никто не узнает, '
        f'пока ты не разрешишь (/pending)'
    )


@stuff.admin_only
@stuff.as_handler(CommandHandler, command='pending')
@stuff.inject(chat=True)
def view_pending_donates(bot: Bot, update: Update, chat: Chat):

    dds = Donate.q.filter(Donate.counts == None).all()

    if dds:
        bot.send_message(
            chat.id,
            templ.get_template('uncounted-donates-list.md').render(donates=dds),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        bot.send_message(chat.id, 'Неподтверждённых нет')


@stuff.admin_only
@stuff.as_handler(RegexHandler, pattern=r'^\d{1,4} (да|нет)$')
@stuff.inject(chat=True, sesh=True)
def accept_reject_donate(bot: Bot, update: Update, chat: Chat, sesh):
    did, verdict = update.message.text.split()
    counts = {'да': True, 'нет': False}[verdict]
    did = int(did)
    d = Donate.q.get(did)
    if not d:
        bot.send_message(chat.id, 'такого доната нет, /pending')
        return
    if d.counts is not None:
        bot.send_message(chat.id, f'этот донат уже был рассмотрен, ныне он {"не " if not d.counts else ""}считается')
        return

    d.counts = counts

    msg = f'донат #{d.id} '
    if not counts:
        msg += 'больше не побеспокоит'
    else:
        rcv_cnt = Chat.q.filter(Chat.muted == False).count()
        msg += f'скоро появится у подписчиков (сейчас их {rcv_cnt})'
    bot.send_message(chat.id, msg)
