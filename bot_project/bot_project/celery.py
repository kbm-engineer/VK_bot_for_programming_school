import os
from datetime import timedelta

from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot_project.settings')

tasks_config = settings.VK

app = Celery('bot_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send_reminder_messages': {
        'task': 'bot_app.tasks.send_reminder_messages',
        'schedule': timedelta(days=tasks_config.get('TASKS_INTERVAL')),
    },
    'mailing': {
        'task': 'bot_app.tasks.mailing',
        'schedule': timedelta(days=tasks_config.get('TASKS_INTERVAL')),
    },
}
