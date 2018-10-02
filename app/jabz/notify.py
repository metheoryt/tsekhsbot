import logging
from telegram import Bot, ParseMode
from app.models import Donate, Chat, ThanksADay
from app import queue, stuff
from app import templ
import sqlalchemy as sa


log = logging.getLogger(__name__)


@stuff.inject(sesh=True)  # только ради автокоммита в конце
def notify_about_new_donate(bot: Bot, job, sesh):

    log.info('let\'s see if we have some fresh donates')
    d = Donate.q.filter(Donate.counts == True, Donate.announced == False).order_by(Donate.date.asc()).first()
    """:type: Donate"""

    if not d:
        log.info('nothing fresh in non-announced donates')
        return

    log.info(f'got fresh {d}')

    receivers = Chat.q.filter(Chat.muted == False).all()
    """:type: list[Chat]"""

    tt = templ.get_template('new-donate.md')

    for r in receivers:
        log.debug(f'notifying {r!r}')
        bot.send_message(
            chat_id=r.id,
            text=tt.render(donate=d, thanks_a_day=ThanksADay.q.order_by(sa.func.random()).first().text),
            parse_mode=ParseMode.MARKDOWN
        )

    # если всё хорошо
    d.announced = True


job_notify = queue.run_repeating(notify_about_new_donate, interval=2*60, first=1*60)
