from django.apps import AppConfig

from bot_app import VERSION

app_version = '.'.join(map(str, VERSION))

class Bot_appConfig(AppConfig):
    name = 'bot_app'
    verbose_name = f'Бот_вк версия: {app_version}'

    def ready(self) -> None:
        from bot_app.tasks import run_bot
        run_bot.delay()
        return super().ready()
