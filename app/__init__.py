from telegram.ext import Updater
import cfg


updater = Updater(token=cfg.BOT_TOKEN)


queue = updater.job_queue


dispatcher = updater.dispatcher
