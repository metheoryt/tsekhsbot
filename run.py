from time import sleep
import logging
import cfg
from app.models import engine, Base, Exchange, DonateAuthor
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
            log.warning(f'cannot connect to db, will try {4-i} more times')
            sleep(3)

    Base.metadata.create_all(engine)
    if not Exchange.q.count() and not DonateAuthor.q.count():
        log.info('fresh install detected, filling DB with static data')
        ramp_up()

    from app import updater

    # активируем диалоги и периодические задания прям перед запуска бота
    from app import dialogs, jabz

    updater.start_polling()
    updater.idle()
