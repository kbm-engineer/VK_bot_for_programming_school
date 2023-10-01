from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from bot_app.logs.logger import logger
from bot_app.message_sender import MyBot
from bot_app.models import Mailing, Reminders, UserInteraction, UserVk
from bot_project.celery import app


MESSAGES = {
    'INTERACTION_NOT_GET': 'Ошибка при получении Напоминаний из БД',
    'BOT_STARTED': 'Бот запущен и работает!',
    'MAILING_NOT_GET': 'Ошибка при получении Mailing из БД или их отсутствие',
    'EXPORT_USERS_XLS_ERROR': 'Ошибка при экспорте пользователей в XLS',
}

conf = settings.VK


@app.task
def send_reminder_messages():
    try:
        logger.info('Задача отправки напоминаний в работе')
        first_reminder_users = UserInteraction.objects.filter(
            last_interaction__lte=timezone.now() - timedelta(
                days=Reminders.objects.get(
                    type=settings.FIRST_REMINDER_TYPE
                ).reminder_days
            ),
            is_first_reminder_sent=False,
            user__is_subscribed=True
        )

        second_reminder_users = UserInteraction.objects.filter(
            last_interaction__lte=timezone.now() - timedelta(
                days=Reminders.objects.get(
                    type=settings.SECOND_REMINDER_TYPE
                ).reminder_days
            ),
            is_second_reminder_sent=False,
            user__is_subscribed=True
        )
    except Exception as error:
        logger.error(MESSAGES['INTERACTION_NOT_GET'])
        logger.error(str(error))
        return

    for interaction in first_reminder_users:
        send_reminder(
            user=interaction.user,
            reminder_type=settings.FIRST_REMINDER_TYPE
        )
        interaction.is_first_reminder_sent = True
        interaction.save(update_fields=['is_first_reminder_sent'])

    for interaction in second_reminder_users:
        send_reminder(
            user=interaction.user,
            reminder_type=settings.SECOND_REMINDER_TYPE
        )
        interaction.is_second_reminder_sent = True
        interaction.save(update_fields=['is_second_reminder_sent'])


def send_reminder(user, reminder_type):
    try:
        reminder = Reminders.objects.get(type=reminder_type)
    except Exception as error:
        logger.error(MESSAGES['INTERACTION_NOT_GET'])
        logger.error(str(error))
        return
    bot = MyBot(token=conf.get('VK_API_TOKEN'), group_id=conf.get('GROUP_ID'))
    unsubscribe_keyboard = bot.create_unsubscribe_keyboard()
    keyboard = unsubscribe_keyboard if reminder.is_unsubscribe_button else None
    bot.send_message(
        user_id=user.user_id,
        message=reminder.reminder_text,
        keyboard=keyboard
    )


@app.task
def mailing():
    logger.info('Задача отправки рассылок')
    TOKEN = conf.get('VK_API_TOKEN')
    bot = MyBot(token=TOKEN, group_id=conf.get('GROUP_ID'))
    try:
        mailing_objects = Mailing.objects.filter(counter__lt=12)
    except Exception as error:
        logger.error(MESSAGES['MAILING_NOT_GET'])
        logger.error(str(error))
        mailing_objects = []

    for mailing_obj in mailing_objects:
        counter_value = mailing_obj.counter
        user_id = mailing_obj.uservk.user_id
        mailing_act = mailing_obj.is_activated
        messages = mailing_obj.messages.order_by('sorted').all()
        message_list = list(messages)
        if len(message_list) > counter_value and len(message_list) != 0 and mailing_act:
            element = message_list[counter_value]
            if len(message_list) == counter_value + 1:
                unsubscribe_keyboard = bot.create_menu_keyboard()
                mailing_obj.unactivate()
            else:
                unsubscribe_keyboard = bot.create_unactivated_mailing_keyboard(
                    type_mailing=mailing_obj.type_mailing)

            bot.send_message(
                user_id=user_id,
                message=element.message,
                keyboard=unsubscribe_keyboard)
            mailing_obj.counter += 1
            mailing_obj.save()
        else:
            mailing_obj.unactivate()


@shared_task
def run_bot():
    TOKEN = conf.get('VK_API_TOKEN')
    GROUP_ID = conf.get('GROUP_ID')
    bot = MyBot(
        token=TOKEN,
        group_id=GROUP_ID,

    )
    bot.run()
    logger.info('Бот запущен и работает!')


@shared_task
def export_users_xls():
    logger.info('Задача экспорта в .xls')
    try:
        user = UserVk.objects.all().count()
        reminder = Reminders.objects.all().count()
        return [user, reminder]
    except Exception as error:
        logger.error(MESSAGES['EXPORT_USERS_XLS_ERROR'])
        logger.error(str(error))
