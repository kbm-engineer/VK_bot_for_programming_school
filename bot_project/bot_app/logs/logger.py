import logging
import os
from logging.handlers import TimedRotatingFileHandler

from django.conf import settings


log_file = os.path.join(os.path.dirname(__file__), 'bot_logs.log')

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

file_handler = TimedRotatingFileHandler(
    log_file,
    when=settings.LOG_SETTINGS['when'],
    interval=settings.LOG_SETTINGS['interval'],
    backupCount=settings.LOG_SETTINGS['backupCount'],
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
