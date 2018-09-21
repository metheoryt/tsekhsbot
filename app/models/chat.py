from . import Base
import sqlalchemy as sa


class Chat(Base):
    """Чаты tg"""

    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    """Уникальный ID чата"""

    name = sa.Column(sa.Text)
