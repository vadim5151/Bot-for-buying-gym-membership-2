import os
from dotenv import load_dotenv


load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
PROXY_URL = os.getenv('PROXY_URL')
PAYMENT_ENDS_CHECK_DELAY = 86400