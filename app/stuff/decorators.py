import logging
from functools import wraps
from app import dispatcher
from app.models import Session, Chat


log = logging.getLogger(__name__)


def with_session(fn):
    """добавляет сессию в хвост позиционных аргументов"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        s = Session()
        try:
            r = fn(*args, s, **kwargs)
            s.commit()
            return r
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()
    return wrapper


def with_chat(fn):
    """добавляет объект чата в хвост позиционных аргументов"""
    @wraps(fn)
    def wrapper(bot, update, *args, **kwargs):
        s = Session()
        if not Chat.q.get(update.message.chat.id):
            chat = Chat(id=update.message.chat.id, is_private=update.message.chat.type == 'private')
            s.add(chat)
            s.commit()
        chat = Chat.q.get(update.message.chat.id)  # type: Chat
        return fn(bot, update, *args, chat, **kwargs)
    return wrapper


def inject(chat=False, sesh=False):
    """Шорткат для with_*"""
    def decorator(fn):
        if sesh:
            fn = with_session(fn)
        if chat:
            fn = with_chat(fn)
        return fn

    return decorator


def as_handler(handler_cls, pass_chat_data=False, **handler_kwargs):
    """
    Добавляет функцию как обработчик (4 уровня!).
    Если обработчик возвращает что-либо кроме None - ожидается продолжение диалога

    :param handler_cls: класс обработчика (CommandHandler, MessageHandler)
    :param pass_chat_data: один из общих параметров обработчиков, проксируемый для удобства
    :param handler_kwargs: ключевые параметры обработчика
    """
    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, chat_data, **kwargs):
            # мэйнтэйним без спросу (pass_chat_data=True ниже), но передаём только по требованию
            if pass_chat_data:
                kwargs['chat_data'] = chat_data

            if chat_data.get('__next_step') is not None:
                # если мы попали в диалог - это уже дело _dialog_catch_all
                return
            else:
                # но мы все равно должны поддерживать возможность начала диалога из любого обработчика
                result = fn(*args, **kwargs)
                chat_data['__prev_step'] = chat_data.get('__next_step')
                chat_data['__next_step'] = result

        dispatcher.add_handler(handler_cls(callback=wrapper, pass_chat_data=True, **handler_kwargs), group=4)
        return wrapper

    return decorator


def admin_only(fn):
    @wraps(fn)
    def wrapper(bot, update, *args, **kwargs):
        c = Chat.q.get(update.message.chat.id)
        if not c.is_admin:
            return
        else:
            return fn(bot, update, *args, **kwargs)

    return wrapper
