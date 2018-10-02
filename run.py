from time import sleep

from app import updater
import logging
import cfg
from app.models import engine, Base, Exchange
from refresh import ramp_up

logging.basicConfig(
    level=getattr(logging, cfg.LOGLEVEL),
    format='%(asctime)s %(levelname)-7s: %(message)s'
)

log = logging.getLogger(__name__)


if __name__ == '__main__':

    for i in range(5):
        try:
            engine.connect()
        except Exception as e:
            if i == 4:
                raise
            log.warning(f'cannot connect to db, will try {4-i} more times ({e!r})')
            sleep(3)

    Base.metadata.create_all(engine)
    if not Exchange.q.count():
        log.info('fresh install detected, filling DB with static data')
        ramp_up()

    updater.start_polling()
    updater.idle()
