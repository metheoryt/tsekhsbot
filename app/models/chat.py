from datetime import datetime

from . import Base
import sqlalchemy as sa


class Chat(Base):
    """Чаты tg"""

    __tablename__ = 'chat'

    id = sa.Column(sa.Integer, primary_key=True)
    """Уникальный ID чата в tg"""

    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)

    is_private = sa.Column(sa.Boolean, nullable=False)
    """не приватный ли чат"""

    is_admin = sa.Column(sa.Boolean, default=False)
    """не со стаффом ли чат"""

    muted = sa.Column(sa.Boolean, default=False)
    """не замьютили ли чат, чтобы не слать уведомления"""

    def __repr__(self):
        return f'<Chat #{self.id} {"" if self.is_private else "non-"}private{" /staff/" if self.is_admin else ""}' \
               f'{" muted" if self.muted else ""}>'
