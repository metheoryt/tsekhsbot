from datetime import datetime
from . import Base
import sqlalchemy as sa


class Donate(Base):
    """Принятые через все источики пожертвования"""

    id = sa.Column(sa.Integer, primary_key=True)

    amount = sa.Column(sa.Numeric(scale=2), nullable=False)

    date = sa.Column(sa.DateTime(), nullable=False, default=datetime.now)

