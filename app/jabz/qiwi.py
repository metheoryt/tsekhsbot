import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pyqiwi import Wallet
from sqlalchemy.orm.exc import NoResultFound
from app.models import Donate, Chat
from app.models.misc import DonateAuthor
from app.stuff import inject
from app import queue
import cfg
from pytz import utc, timezone


log = logging.getLogger(__name__)


msk = timezone('Europe/Moscow')


w = Wallet(token=cfg.QIWI_TOKEN, number=cfg.QIWI_NUMBER)


_month = timedelta(days=60)
_sec = timedelta(seconds=2)


@inject(sesh=True)
def fetch_donates(bot, job, s):
    last_qiwi = Donate.q.filter(
        Donate.source == Donate.Source.QIWI,
    ).order_by(Donate.date.desc()).first()

    # Все входящие операции за либо последний месяц, либо промежуток
    # от даты последней транзакции до сейчас

    start_date = last_qiwi.date - _sec if last_qiwi else datetime.utcnow() - _month
    now = datetime.utcnow()

    log.info('querying qiwi')

    # ! обёртка api форсит часовой пояс UTC+3, а у нас всё в UTC+0, подстраиваемся
    msk_start = msk.fromutc(start_date)
    msk_now = msk.fromutc(now)
    h = w.history(
        rows=40,
        operation='IN',
        start_date=msk_start,
        end_date=msk_now
    )

    ts = h['transactions']
    """:type: list[pyqiwi.types.Transaction]"""

    changes = False

    for t in ts[::-1]:
        log.info(f'checking ts #{t.txn_id}')
        try:
            Donate.q.filter(Donate.txn_id == t.txn_id).one()
        except NoResultFound:
            phone = str(t.account)
            try:
                a = DonateAuthor.q.filter(DonateAuthor.phone == phone).one()
            except NoResultFound:
                a = DonateAuthor(phone=phone)
                s.add(a)
                s.commit()
                log.info(f'added new {a!r}')

            new_donate = Donate(
                txn_id=t.txn_id,
                source=Donate.Source.QIWI,
                date=utc.normalize(t.date).replace(tzinfo=None),  # приводим к UTC и удаляем tz
                amount=Decimal(t.total.amount),
                currency=Donate.Currency(t.total.currency),
                author=a
            )

            s.add(new_donate)
            log.info(f'added fresh {new_donate!r}')
            changes = True
    if changes:
        admins = Chat.q.filter(Chat.is_admin == True, Chat.muted == False).all()
        for ac in admins:
            bot.send_message(ac.id, 'Новые донаты! /pending')


# стартует через 20 секунд после запуска
job_fetch_donates = queue.run_repeating(fetch_donates, interval=cfg.QIWI_FETCH_INTERVAL, first=20)
