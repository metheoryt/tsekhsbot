from functools import wraps
from sqlalchemy.orm import Session
from app import dispatcher
from app.models import Chat


def with_session(fn):
    """добавляет сессию в хвост позиционных аргументов"""
    @wraps(fn)
    def wrapper(bot, update_or_job, *args, **kwargs):
        s = Session()
        try:
            r = fn(bot, update_or_job, *args, s, **kwargs)
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


def as_handler(handler_cls, pass_chat_data=False, **handler_kwargs):
    """
    Добавляет функцию как обработчик.
    :param handler_cls: класс обработчика (CommandHandler, MessageHandler)
    :param handler_kwargs: ключевые параметры обработчика
    :return:
    """
    def decorator(fn):

        @wraps(fn)
        def wrapper(bot, update_or_job, *args, chat_data, **kwargs):
            # мэйнтэйним без спросу (pass_chat_data=True ниже), но передаём только по требованию
            if pass_chat_data:
                kwargs['chat_data'] = chat_data

            if chat_data.get('__next_step') is not None:
                # если мы попали в диалог - это уже дело _dialog_catch_all
                return
            else:
                # но мы все равно должны поддерживать возможность начала диалога из любого обработчика
                result = fn(bot, update_or_job, *args, **kwargs)
                chat_data['__prev_step'] = chat_data.get('__next_step')
                chat_data['__next_step'] = result

        dispatcher.add_handler(handler_cls(callback=wrapper, pass_chat_data=True, **handler_kwargs))
        return wrapper

    return decorator


def admin_only(fn):

    @wraps(fn)
    @with_chat
    def wrapper(bot, upd_or_job, chat, *args, **kwargs):
        if not chat.is_admin:
            return
        else:
            return fn(bot, upd_or_job, *args, **kwargs)
