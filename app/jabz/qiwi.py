import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pyqiwi import Wallet
import pyqiwi
from sqlalchemy.orm.exc import NoResultFound
from app.models import Donate
from app.stuff import inject
from app import queue
import cfg


log = logging.getLogger(__name__)


w = Wallet(token=cfg.QIWI_TOKEN, number=cfg.QIWI_NUMBER)


_month = timedelta(days=31)
_sec = timedelta(seconds=2)


@inject(sesh=True)
def fetch_donates(bot, job, s):
    last_qiwi = Donate.q.filter(
        Donate.source == Donate.Source.QIWI,
    ).order_by(Donate.date.desc()).first()

    start_date = last_qiwi.date -_sec if last_qiwi else datetime.now() - _month

    # Все входящие операции за либо последний месяц, либо промежуток
    # от даты последней транзакции до сейчас
    h = w.history(rows=100, operation='IN', start_date=start_date, end_date=datetime.now())

    ts = h['transactions']
    """:type: list[pyqiwi.types.Transaction]"""

    for t in ts:
        log.info(f'checking ts #{t.txn_id}')
        try:
            Donate.q.filter(Donate.txn_id == t.txn_id).one()
        except NoResultFound:
            new_donate = Donate(
                extid=t.txn_id,
                source=Donate.Source.QIWI,
                date=t.date,
                amount=Decimal(t.total.amount),
                currency=Donate.Currency(t.total.currency),
                author_phone=str(t.account) if t.account else None
            )
            log.info(f'adding fresh {new_donate!r}')
            s.add(new_donate)


# Пусть работает каждые 5 минут
job_fetch_donates = queue.run_repeating(fetch_donates, interval=60*5, first=30*3)
