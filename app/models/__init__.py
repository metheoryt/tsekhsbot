from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
import cfg


engine = create_engine(cfg.DB_DSN, echo=cfg.DB_ECHO)
Session = scoped_session(sessionmaker(bind=engine))


_Base = declarative_base()


class Base(_Base):

    __abstract__ = True

    q = Session.query_property()


def with_session(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        s = Session()
        try:
            r = fn(s, *args, **kwargs)
            s.commit()
            return r
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()
    return wrapper


from .chat import User
