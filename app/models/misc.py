from . import Base
import sqlalchemy as sa


class DonateAuthor(Base):
    __tablename__ = 'donate_author'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.Text, nullable=True)
    phone = sa.Column(sa.Text, nullable=True)

    @property
    def introduce(self):
        if self.name:
            if len(self.name.split()) > 1:
                return f'{self.name.split()[0]} {self.name.split()[1][0]}.'
            else:
                return self.name
        elif self.phone:
            return f'инкогнито ({self.phone[:-4]}...)'
        else:
            return 'инкогнито'

    def __repr__(self):
        return f'<DonateAuthor #{self.id} name={self.name} phone={self.phone}'


class ThanksADay(Base):
    """Такой-то закинул денег, за что ему {{thanks_a_day}}!"""

    __tablename__ = 'thanks_a_day'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.Text, nullable=False)


class Exchange(Base):

    __tablename__ = 'exchange'

    id = sa.Column(sa.Integer, primary_key=True)
    """Код валюты"""

    rate = sa.Column(sa.Float, nullable=False)
    """Курс относительно одной валюты, здесь это KZT"""
