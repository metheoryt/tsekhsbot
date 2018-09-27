from datetime import datetime
from . import Base
import sqlalchemy as sa
import sqlalchemy_utils as su
from enum import Enum


class DonateSource(Enum):

    QIWI = 'qiwi'
    CASH = 'cash'


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

    txn_id = sa.Column(sa.Integer(), unique=True, nullable=True)

    amount = sa.Column(sa.Numeric(scale=2), nullable=False)

    currency = sa.Column(su.ChoiceType(Currency, impl=sa.Integer()), nullable=False, default=Currency.KZT)

    date = sa.Column(sa.DateTime(), nullable=False, default=datetime.now)

    announced = sa.Column(sa.Boolean(), nullable=False, default=False)
    """Было ли отправлено по этому пожертвованию уведомление"""

    source = sa.Column(su.ChoiceType(DonateSource, impl=sa.Text()), nullable=False, default=DonateSource.CASH)
    """Источник доната. По умолчанию это личные переводы"""

    author_name = sa.Column(sa.Text)
    """Его имя, если есть"""

    author_phone = sa.Column(sa.Text)
    """Его телефон, если есть"""

    @property
    def masked_phone(self):
        return f'{self.author_phone[:7]}xxxxx' if self.author_phone and len(self.author_phone) > 7 else None

    counts = sa.Column(sa.Boolean, nullable=True, default=None)
    """Считается ли пожертвование за пожертвование. None если это ещё не определено"""

    @property
    def _ago(self):
        p = datetime.now() - self.date
        return f'{p.days}d{p.seconds // 3600}h{p.seconds // 60}m'

    def __repr__(self):
        return f'<Donate {self.amount}{self.currency.name} #{self.txn_id} < {self.author_name or self.author_phone} ' \
               f'({self.source.name}) {self._ago} ago {"(fresh)" if not self.announced else ""}'
