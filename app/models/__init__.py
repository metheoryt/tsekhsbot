from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import cfg


engine = create_engine(cfg.DB_DSN, echo=cfg.DB_ECHO)


Session = scoped_session(sessionmaker(bind=engine))


_Base = declarative_base()


class Base(_Base):

    __abstract__ = True

    q = Session.query_property()


from .chat import Chat
from .donate import Donate
from .misc import ThanksADay
