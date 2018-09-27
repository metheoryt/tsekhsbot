from telegram.ext import Updater
import cfg
from jinja2 import Environment, PackageLoader, select_autoescape


class DaEnv(Environment):

    def __init__(self, *args, **kwargs):
        super(DaEnv, self).__init__(*args, **kwargs)
        self.globals['cfg'] = cfg


templ = DaEnv(
    loader=PackageLoader('app', 'tpl'),
    autoescape=select_autoescape(['md'])
)

updater = Updater(token=cfg.BOT_TOKEN)


queue = updater.job_queue


dispatcher = updater.dispatcher


from . import dialogs, jabz
