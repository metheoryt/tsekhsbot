from app import updater
import logging
import cfg

logging.basicConfig(
    level=getattr(logging, cfg.LOGLEVEL),
    format='%(asctime)s %(levelname)-7s: %(message)s'
)


if __name__ == '__main__':

    updater.start_polling()
    updater.idle()
