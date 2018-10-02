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
    Base.metadata.create_all(engine)
    if not Exchange.q.count():
        log.info('fresh install detected, filling DB with static data')
        ramp_up()

    updater.start_polling()
    updater.idle()
