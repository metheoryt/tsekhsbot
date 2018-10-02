from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.hybrid import hybrid_property

from app.models import Exchange
from . import Base
import sqlalchemy as sa
import sqlalchemy_utils as su
from enum import Enum
from pytz import utc
from sqlalchemy.orm import relation


class DonateSource(Enum):

    QIWI = 'qiwi'
    CASH = 'карман'


class Currency(Enum):

    KZT = 398
    RUR = 643
    USD = 840


class Donate(Base):
    """Принятые через все источики пожертвования"""
    __tablename__ = 'donate'

    Currency = Currency
    Source = DonateSource

    id = sa.Column(sa.Integer(), primary_key=True)

    amount = sa.Column(sa.Numeric(scale=2), nullable=False)

    currency = sa.Column(su.ChoiceType(Currency, impl=sa.Integer()), sa.ForeignKey('exchange.id'), nullable=False, default=Currency.KZT)
    kzt_exchange = relation('Exchange', uselist=False, lazy='joined')

    date = sa.Column(sa.DateTime(), nullable=False, default=datetime.utcnow)
    source = sa.Column(su.ChoiceType(DonateSource, impl=sa.Text()), nullable=False, default=DonateSource.CASH)
    """Источник доната. По умолчанию это личные переводы"""
    announced = sa.Column(sa.Boolean(), nullable=False, default=False)
    """Было ли отправлено по этому пожертвованию уведомление"""
    counts = sa.Column(sa.Boolean, nullable=True, default=None)
    """Считается ли пожертвование за пожертвование. None если это ещё не определено"""

    txn_id = sa.Column(sa.BigInteger(), unique=True, nullable=True)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('donate_author.id'), nullable=False, default=1)

    author = relation('DonateAuthor', uselist=False, lazy='joined')

    @hybrid_property
    def in_kzt(self):
        return self.amount * Decimal(self.kzt_exchange.rate)

    @in_kzt.expression
    def in_kzt(cls):
        return cls.amount * select([Exchange.rate]).where(Exchange.id == cls.currency).as_scalar()

    @property
    def _ago(self):
        p = datetime.utcnow() - self.date if self.date else 'new'
        ago = ''
        hours = p.seconds // 3600
        minutes = (p.seconds - hours * 3600) // 60
        seconds = (p.seconds - hours * 3600 - minutes * 60)

        if p.days:
            ago += f'{p.days}d'
        if hours:
            ago += f'{hours}h'
        if minutes:
            ago += f'{minutes}m'
        if p.seconds < 60 and not p.days:
            ago += f'{seconds}s'
        return ago

    def __repr__(self):
        return f'<Donate {self.amount}{self.currency.name} #{self.txn_id} < {self.author.name or self.author.phone} ' \
               f'({self.source.value}) {self.date.strftime("%d/%m/%y %H:%m")} ({self._ago}) ago ' \
               f'{"(not announced)" if not self.announced else ""}>'
