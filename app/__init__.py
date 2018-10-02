from telegram.ext import Updater
import cfg
from jinja2 import Environment, PackageLoader, select_autoescape
import pytz
import re


localtz = pytz.timezone(cfg.LOCAL_TZ)


templ = Environment(
    loader=PackageLoader('app', 'tpl'),
    autoescape=select_autoescape(['md'])
)
templ.globals['cfg'] = cfg

templ.filters['localtz'] = lambda x: localtz.fromutc(x).strftime('%d/%m/%y %H:%M:%s')
templ.filters['unmd'] = lambda x: re.sub(r'[_*`\[\]]+', '', x)
templ.filters['int'] = int


updater = Updater(token=cfg.BOT_TOKEN)
bot = updater.bot
queue = updater.job_queue
dispatcher = updater.dispatcher
