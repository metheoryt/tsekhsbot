from . import Base
import sqlalchemy as sa


class ThanksADay(Base):
    """Такой-то закинул денег, за что ему {{thanks_a_day}}!"""

    __tablename__ = 'thanks_a_day'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    text = sa.Column(sa.Text, nullable=False)
