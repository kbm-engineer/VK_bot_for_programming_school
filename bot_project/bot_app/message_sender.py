import time

import vk_api
from django.conf import settings
from django.utils import timezone
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from bot_app.logs.logger import logger
from bot_app.models import (
    Mailing, Mailing_message, Message, UserInteraction, UserVk
)
from bot_app.quiz_data import QUIZ_RESULTS, QUIZ_QUESTIONS
from bot_app.utils import get_user_data, get_group_admins_id, get_corse_message


#TODO: Задавать сообщения через БД
MESSAGES = {
    'HELLO_MESSAGE': 'Привет, {first_name}! Добро пожаловать!',
    'MESSAGE_NOT_SENT': 'Не удалось отправить сообщение пользователю: \
        ID: {user_id}, {error}',
    'ERROR_PROCESSING_MESSAGE': 'Ошибка обработки сообщения: {error}',
    'MESSAGE_NOT_IN_UTF': 'Ошибка декодирования сообщения {message}, {error}',
    'USER_SUBSCRIBE': 'Новый пользователь - ID: {user_id}, Имя: {first_name}',
    'USER_UNSUBSCRIBE': 'Пользователь {user} отписался от рассылки и \
        уведомлений',
    'YOU_UNSUBSCRIBE': 'Вы успешно отписались от уведомлений. Желаем удачи!',
    'MAILING_UNACTIVATED': 'Вы успешно отписались от рассылки. Желаем удачи!',
    'YOU_ALREDY_UNSUBSCRIBE': 'Вы уже отписаны или не были подписаны ранее.',
    'MESSAGE_TO_ADMIN': 'Ваше сообщение передано администратору и он скоро \
        Вам ответит.',
    'ADMIN_HELP': 'Пользователю нужна помощь, текст сообщения: \
        "{message_text}" ссылка на диалог с пользователем: {url}',
    'ONLY_TEXT_COMMANDS': 'Поддерживаются только текстовые комманды',
    'INTERACTION_NOT_UPDATE': 'Не удалось создать или обновить дату \
        взаимодействия пользователя с ботом!',
    'MESSAGE_NOT_UPDATE': 'Не удалось создать или обновить сообщения \
        пользователя с ID: {user_id} в БД!',
    'SEND_MESSAGE_FROM_BOT': 'Пользователю с ID: {user_id} отправленно \
        сообщение {message}',
    'HELP_MESSAGE': 'Привет, вот список комманд которые я могу распознать:\
        \nМЕНЮ,\nНАПРАВЛЕНИЯ,\nПРОГРАММИРОВАНИЕ,\nРОБОТОТЕХНИКА,\n\
        ТЕСТИРОВАНИЕ,\nОТПИСАТЬСЯ',
    'QUIZ_COMPLITE': 'У ребёнка есть талант к программированию, \
        робототехнике и творчеству , и он готов продолжать обучение и \
        развиваться в этой области. Его способности, умения и навыки \
        необходимы для создания интересных и полезных проектов, \
        приложений и игр.'
}
#TODO: Реализовать через БД, хранить историю опросов
QUIZ_USERS = {}


def empty_quiz_users(user_id):
    try:
        QUIZ_USERS.pop(user_id)
    except Exception:
        pass
    return


class BaseBot:
    def __init__(self, token, group_id):
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)

    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    self.message_handler(event)
                except vk_api.exceptions.VkApiError as error:
                    #TODO: Отправить сообщение об на email администратора
                    logger.error(
                        MESSAGES['ERROR_PROCESSING_MESSAGE'].format(
                            error=error
                        )
                    )

    def message_handler(self, data):
        pass


class MyBot(BaseBot):
    def __init__(self, token, group_id):
        super().__init__(token, group_id)
        self.answered_users = {}

    conf = settings.VK

    message_courses = get_corse_message()

    #TODO: Задавать комманды через БД
    command_mailer = [
        'ПРОГРАММИРОВАНИЕ',
        'РОБОТОТЕХНИКА'
    ]
    command_quiz = ('ТЕСТИРОВАНИЕ', 'A', 'B', 'C')
    command_help = (
        'ПОМОЩЬ', 'СПРАВКА', 'HELP', 'H', 'КОММАНДЫ',
        'ОТВЕТЬ', 'ПРИВЕТ', 'ХАЙ', 'HI', 'HELLO', 'HEY'
    )
    command_handlers = {
        'МЕНЮ': ['create_menu_keyboard', 'Выберите пункт меню:'],
        'НАПРАВЛЕНИЯ': [
            'create_menu_keyboard_directions',
            'Выберите направление:'
        ],
        command_mailer[0]: [
            'create_menu_keyboard_program',
            'Запишитесь на пробный урок по программированию,\
                или ознакомьтесь подробнее с другими нашими курсами'
        ],
        command_mailer[1]: [
            'create_menu_keyboard_robototeh',
            'Запишитесь на пробный урок по робототехнике, \
                или ознакомьтесь подробнее с другими нашими курсами'
        ],
        'УЗНАТЬ ВСЕ О НАШИХ НАПРАВЛЕНИЯХ': [
            'create_menu_feedback',
            message_courses
        ],
        'ОТПИСАТЬСЯ': ['handle_unsubscribe', 'ОТПИСАТЬСЯ'],
        'ОТПИСАТЬСЯ ОТ РАССЫЛКИ ПРОГРАММИРОВАНИЕ': [
            'handle_unactivate',
            'ОТПИСАТЬСЯ ОТ РАССЫЛКИ ПРОГРАММИРОВАНИЕ'],
        'ОТПИСАТЬСЯ ОТ РАССЫЛКИ ПО РОБОТОТЕХНИКЕ': [
            'handle_unactivate',
            'ОТПИСАТЬСЯ ОТ РАССЫЛКИ ПО РОБОТОТЕХНИКЕ'],
    }

    def message_handler(self, data):
        '''Метод обработчик входящих сообщений'''
        message_user = ''
        user_id = data.object.message.get('from_id')
        user_data = self.vk.users.get(
            fields=('city', 'contacts', 'bdate'),
            user_id=user_id)[0]
        message_text = data.object.message.get('text').upper()
        try:
            decoded_message_text = message_text.encode(
                'utf-8').decode('utf-8')
        except UnicodeDecodeError as error:
            logger.error(MESSAGES['MESSAGE_NOT_IN_UTF'].format(
                error=error, message=decoded_message_text
            ))
            self.send_message(
                user_id=user_id,
                message=MESSAGES['ONLY_TEXT_COMMANDS']
            )
            return

        count_messages = self.vk.messages.getHistory(
            user_id=user_id).get('count')
        if count_messages < 2:
            user_data = self.vk.users.get(
                fields=('city', 'contacts', 'bdate'),
                user_id=user_id)[0]
            first_name = user_data.get('first_name')
            message_user = MESSAGES['HELLO_MESSAGE'].format(
                first_name=first_name
            )
            logger.info(
                MESSAGES['USER_SUBSCRIBE'].format(
                    user_id=user_id, first_name=first_name
                )
            )
            keyboard = self.create_menu_keyboard()

        elif message_text in self.command_help:
            keyboard = self.create_menu_keyboard()
            message_user = MESSAGES['HELP_MESSAGE']
            empty_quiz_users(user_id)
            self.create_or_update_last_interaction(user_data, message_text)
            self.send_message(
                user_id=user_id, message=message_user, keyboard=keyboard
            )
            return

        elif message_text in self.command_quiz:
            keyboard = self.create_menu_quiz()
            if user_id in QUIZ_USERS:
                if message_text == self.command_quiz[0]:
                    empty_quiz_users(user_id)
                    self.create_or_update_last_interaction(
                        user_data, message_text
                    )
                    keyboard = self.create_menu_keyboard()
                    self.send_message(
                        user_id=user_id,
                        message='Вы вышли из тестирования, результаты \
                            не сохранены.',
                        keyboard=keyboard
                    )
                    return
                if message_text == 'A':
                    result = QUIZ_RESULTS[QUIZ_USERS[user_id][1]]
                elif message_text == 'B':
                    result = QUIZ_RESULTS[QUIZ_USERS[user_id][2]]
                else:
                    result = QUIZ_RESULTS[QUIZ_USERS[user_id][3]]
                self.send_message(
                    user_id=user_id, message=result, keyboard=None
                )

                if QUIZ_USERS[user_id][0] == len(QUIZ_QUESTIONS):
                    self.mailing(
                        user_id=user_id, type_mailing=self.command_mailer[0]
                    )
                    keyboard = self.create_menu_keyboard()
                    empty_quiz_users(user_id)
                    self.send_message(
                        user_id=user_id,
                        message=MESSAGES['QUIZ_COMPLITE'],
                        keyboard=keyboard
                    )
                    return
                QUIZ_USERS[user_id][0] += 1
                #TODO: перенести в БД
                time.sleep(self.conf.get('QUIZ_RESPONSE_INTERVAL'))
                self.quiz_message(user_id, keyboard)
            else:
                self.create_or_update_last_interaction(
                    user_data, message_text
                )
                QUIZ_USERS[user_id] = [1, ]
                self.quiz_message(user_id, keyboard)
            return
        elif message_text in self.command_handlers:
            if message_text == self.command_handlers[message_text][1]:
                empty_quiz_users(user_id)
                self.create_or_update_last_interaction(
                    user_data, message_text
                )
                self.handle_unsubscribe(user_id, message_text)
                return
            else:
                if message_text in self.command_mailer:
                    self.mailing(user_id=user_id, type_mailing=message_text)
                handler_name = self.command_handlers[message_text]
                keyboard = getattr(self, handler_name[0])()
                message_user = handler_name[1]
        else:
            keyboard = self.create_menu_keyboard()
            if user_id in self.answered_users:
                message_user = 'Выберите пункт меню'
            else:
                admins_id = get_group_admins_id()
                message_user = MESSAGES['MESSAGE_TO_ADMIN']
                message_admin = MESSAGES['ADMIN_HELP'].format(
                    message_text=message_text,
                    url=f'https://vk.com/im?sel={user_id}'
                )
                for admin_id in admins_id:
                    self.send_message(user_id=admin_id, message=message_admin)
                self.answered_users[user_id] = True
        empty_quiz_users(user_id)
        self.create_or_update_last_interaction(user_data, message_text)
        self.send_message(
            user_id=user_id, message=message_user, keyboard=keyboard
        )

    def send_message(self, user_id, message, keyboard=None):
        '''Универсальный метод отправки сообщений'''
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard() if keyboard else None
            )
            logger.info(
                MESSAGES['SEND_MESSAGE_FROM_BOT'].format(
                    user_id=user_id, message=message
                )
            )
        except vk_api.exceptions.VkApiError as error:
            logger.error(
                MESSAGES['MESSAGE_NOT_SENT'].format(
                    error=error, user_id=user_id
                )
            )
        return

    def create_menu_keyboard(self):
        '''Метод для создания основного меню'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Направления', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Тестирование', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_openlink_button(
            'Товары',
            'https://vk.com/market-183287343'
        )
        keyboard.add_openlink_button(
            'Обратная связь',
            'https://vk.com/app5619682_-183287343')
        return keyboard

    def create_menu_keyboard_directions(self):
        '''Метод для создания меню Направления'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(
            'Программирование',
            color=VkKeyboardColor.PRIMARY
        )
        keyboard.add_button(
            'Робототехника',
            color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_openlink_button(
            'Узнать о всех наших направлениях',
            'https://vk.com/market-183287343?section=album_2'
        )
        return keyboard

    def create_menu_keyboard_program(self):
        '''Метод для создания меню Программирование'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_openlink_button(
            'Записаться на пробный урок',
            'https://vk.com/app5619682_-183287343#519407')
        keyboard.add_openlink_button(
            'Наши курсы',
            'https://vk.com/market-183287343?section=album_2')
        return keyboard

    def create_menu_keyboard_robototeh(self):
        '''Метод для создания меню Робототехника'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_openlink_button(
            'Записаться на пробный урок',
            'https://vk.com/app5619682_-183287343#519407')
        keyboard.add_openlink_button(
            'Наши курсы по робототехнике',
            'https://vk.com/market-183287343?section=album_2')
        return keyboard

    def create_menu_feedback(self):
        '''Метод для создания меню Обратная связь'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_openlink_button(
            'Обратная связь',
            'https://vk.com/app5619682_-183287343')
        keyboard.add_button('Меню', color=VkKeyboardColor.NEGATIVE)
        return keyboard

    def create_unsubscribe_keyboard(self):
        '''Метод для создания клавиатуры с кнопкой "Отписаться"'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Отписаться', color=VkKeyboardColor.NEGATIVE)
        return keyboard

    def create_menu_quiz(self):
        '''Метод для создания ответов тестирования'''
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('A', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('B', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('C', color=VkKeyboardColor.PRIMARY)
        return keyboard

    def create_unactivated_mailing_keyboard(self, type_mailing):
        '''Метод для создания клавиатуры с кнопкой "Отписаться"'''
        keyboard = VkKeyboard(one_time=True)
        if type_mailing == 'ПРОГРАММИРОВАНИЕ':
            keyboard.add_button(
                'Отписаться от рассылки Программирование',
                color=VkKeyboardColor.NEGATIVE)
        else:
            keyboard.add_button(
                'Отписаться от рассылки по робототехнике',
                color=VkKeyboardColor.NEGATIVE)
        return keyboard

    def handle_unsubscribe(self, user_id, message_text):
        '''Обработка Отписки - отмечаем юзера неподписанным'''
        try:
            if message_text == 'ОТПИСАТЬСЯ':
                user = UserVk.objects.get(user_id=user_id)
                user.unsubscribe()
                message = MESSAGES['YOU_UNSUBSCRIBE']
            else:
                if message_text == 'ОТПИСАТЬСЯ ОТ РАССЫЛКИ ПРОГРАММИРОВАНИЕ':
                    type_mailing = self.command_mailer[0]
                else:
                    type_mailing = self.command_mailer[1]
                mailing = Mailing.objects.get(
                    uservk__user_id=user_id,
                    type_mailing=type_mailing,
                    is_activated=True)
                mailing.unactivate()
                message = MESSAGES['MAILING_UNACTIVATED']
        except Exception as error:
            logger.error(f'Ошибка при попытке отписаться от рассылок: {error}')
            message = MESSAGES['YOU_ALREDY_UNSUBSCRIBE']

        self.send_message(user_id=user_id, message=message, keyboard=None)

    def create_or_update_last_interaction(self, user_data, message):
        '''Обновление времени последнего взаимодействия с пользователем'''
        try:
            user_data = get_user_data(user_data)
            user, _ = UserVk.objects.get_or_create(**user_data)

            user_interaction, _ = (
                UserInteraction.objects.get_or_create(user=user)
            )
            user_interaction.last_interaction = timezone.now()
            user_interaction.is_first_reminder_sent = False
            user_interaction.is_second_reminder_sent = False
            user_interaction.save()

            Message.objects.create(uservk=user, message=message)
        except Exception as error:
            logger.error(
                MESSAGES['INTERACTION_NOT_UPDATE']
            )
            logger.error(str(error))

    def mailing(self, user_id, type_mailing):
        try:
            user = UserVk.objects.get(user_id=user_id)
            mailing = Mailing.objects.filter(
                uservk=user,
                is_activated=True,
                type_mailing=type_mailing)
            if mailing:
                logger.info(
                    "Рассылка уже существует для данного пользователя.")
                return
            new_mailing = Mailing.objects.create(
                uservk=user, type_mailing=type_mailing
            )
            messages_for_mailing = Mailing_message.objects.filter(
                message_type=type_mailing).order_by('sorted')[:12]
            new_mailing.messages.add(*messages_for_mailing)
        except Exception as error:
            logger.error(
                MESSAGES['MESSAGE_NOT_UPDATE'].format(user_id=user_id)
            )
            logger.error(str(error))

    def quiz_message(self, user_id, keyboard):
        quiz_text = QUIZ_QUESTIONS[QUIZ_USERS[user_id][0] - 1]
        quiz_answers = ''
        for answer_lst in quiz_text.values():
            for answer in answer_lst:
                quiz_answers +=  answer + '\n'
                QUIZ_USERS[user_id].append(answer)
        self.send_message(
            user_id=user_id,
            message=f'Вопрос:\n{list(quiz_text.keys())[0]}',
            keyboard=None
        )
        self.send_message(
            user_id=user_id,
            message=f'Варианты ответов:\n{quiz_answers}',
            keyboard=keyboard
        )
