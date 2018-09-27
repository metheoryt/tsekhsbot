from telegram import Bot, Update
from telegram.ext import MessageHandler, Filters
from app import dispatcher


_conversation_handlers = {}


def _dialog_catch_all(bot: Bot, update_or_job, chat_data: dict):
    next_step = chat_data.get('__next_step')
    if next_step:
        # ожидается ответ
        try:
            result = _conversation_handlers[next_step](bot, update_or_job, chat_data=chat_data)
        except Exception:
            # если не удалось обработать обновление - остаёмся на том же шаге
            if isinstance(update_or_job, Update):
                bot.send_message(update_or_job.message.chat.id, 'эм..')
            raise
        else:
            chat_data['__prev_step'] = next_step
            chat_data['__next_step'] = result


def dialog_part(step: str):
    """Помечает функцию как часть диалога (см. обработчик _dialog_catch_all).
    Может использоваться с остальными декораторами, но должна быть в основном наверху.


    Декорируемая функция должна принимать chat_data

    :param step: шаг, на котором выполняется обработчик
    """

    def decorator(fn):

        if not _conversation_handlers:
            # при добавлении первого обработчика
            # добавляем в отдельный (более приоритетный) канал catch-all для диалогов
            dispatcher.add_handler(MessageHandler(Filters.all, _dialog_catch_all, pass_chat_data=True), group=2)

        _conversation_handlers[step] = fn

        return fn

    return decorator
