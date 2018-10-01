from sqlalchemy import text

from app import stuff
from app.models import Chat, Donate, DonateAuthor
from telegram import Bot, Update, ParseMode
from telegram.ext import CommandHandler
import logging
from sqlalchemy.sql import functions as fn
from app import templ


log = logging.getLogger(__name__)


# все активные донаты, группируются по автору
chart_query = Donate.q.join(DonateAuthor).\
    with_entities(fn.sum(Donate.in_kzt).label('total'), DonateAuthor).\
    filter(Donate.counts == True).\
    group_by(DonateAuthor).\
    order_by(text('total DESC'))


def generate_chart(limit: int):
    d = chart_query.all()
    other_sum = None
    other_authors_count = None
    if len(d) > limit:  # чарт для первых X, остальные суммируются
        d, other = d[:limit], d[limit:]
        other_sum = sum([amount for amount, author in other])
        other_authors_count = len(set([author.id for amount, author in other]))

    return d, other_sum, other_authors_count


@stuff.as_handler(CommandHandler, command='chart')
@stuff.inject(chat=True)
def get_chart(bot: Bot, update: Update, chat: Chat, sesh):
    """Чарт состоит из 5 самых щедрых донатеров
    Учитываются активные донаты со всех источников и по всем валютам (курс примерный)
    Остальные показываются в общей сумме
    """
    chart, other_sum, other_author_count = generate_chart(5)

    tt = templ.get_template('chart.md')

    bot.send_message(
        chat.id,
        tt.render(chart=chart, other_sum=other_sum, other_author_count=other_author_count),
        parse_mode=ParseMode.MARKDOWN
    )
