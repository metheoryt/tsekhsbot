from dotenv import load_dotenv
from os import environ as e


load_dotenv()


r = lambda x: e[x]
o = lambda x, y=None: e.get(x, y)


BOT_TOKEN = r('BOT_TOKEN')
QIWI_TOKEN = r('QIWI_TOKEN')
QIWI_NUMBER = r('QIWI_NUMBER')
LOGLEVEL = o('LOGLEVEL', 'INFO')
DB_DSN = r('DB_DSN')
DB_ECHO = True if o('DB_ECHO') == 'true' else False
