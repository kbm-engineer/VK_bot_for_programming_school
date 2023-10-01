from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


TYPE_CHOICES = (
    ('ПРОГРАММИРОВАНИЕ', 'ПРОГРАММИРОВАНИЕ'),
    ('РОБОТОТЕХНИКА', 'РОБОТОТЕХНИКА'),
)

class AdminData(models.Model):
    admin_id = models.IntegerField(
        unique=True,
        verbose_name='Индентификатор администратора',
        help_text='Введите индентификатор администратора'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы сообщества'


class MessageCourses(models.Model):
    message = models.TextField(
        unique=True,
        verbose_name='Сообщение администратора',
        help_text='Введите сообщение администратора'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Сообщение администратора'
        verbose_name_plural = 'Сообщения администратора'


class UserVk(models.Model):
    user_id = models.IntegerField(
        unique=True,
        verbose_name='VK id',
        help_text='Введите индентификатор пользователя')
    first_name = models.CharField(
        verbose_name='Имя',
        help_text='Введите свое имя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        help_text='Введите свою фамилию',
        max_length=150
    )
    city = models.CharField(
        verbose_name='Город',
        help_text='Введите свой город',
        max_length=150,
        blank=True,
        null=True
    )
    birthday = models.DateField(
        verbose_name='День рождения',
        help_text='Введите дату дня рождения',
        blank=True,
        null=True
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Телефонный номер',
        help_text='Введите Ваш телефонный номер'
    )
    is_subscribed = models.BooleanField(
        default=True,
        verbose_name='Подписка',
        help_text=(
            'Показывает, подписан ли пользователь на уведомления и рассылки'
        ),
    )

    def unsubscribe(self):
        self.is_subscribed = False
        self.save()
        return

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class UserInteraction(models.Model):
    user = models.ForeignKey(
        'UserVk',
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name='Пользователь',
    )
    first_interaction = models.DateTimeField(
        default=timezone.now,
        verbose_name=('Дата первого взаимодействия'),
        help_text=(
            'Показывает, когда пользователь '
            'взаимодействовал с ботом первый раз'
        )
    )
    last_interaction = models.DateTimeField(
        default=timezone.now,
        verbose_name=('Дата последнего взаимодействия'),
        help_text=(
            'Показывает, когда пользователь '
            'взаимодействовал с ботом последний раз'
        )
    )
    is_first_reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Первое напоминание отправлено',
        help_text='Показывает, было ли отправлено первое напоминание',
    )
    is_second_reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Второе напоминание отправлено',
        help_text='Показывает, было ли отправлено второе напоминание',
    )

    class Meta:
        verbose_name = 'Взаимодействие с ботом'
        verbose_name_plural = 'Взаимодействия с ботом'


class Message(models.Model):
    uservk = models.ForeignKey(
        UserVk, default=None,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    message_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='тип сообщения',
        help_text='Введите тип сообщения'
    )
    message = models.TextField(
        verbose_name='Сообщение пользователей',
        blank=True,
        help_text=(
            'Введите сообщение, '
            'которое надо отправить'
        )
    )
    vk_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания сообщения'
    )
    answered = models.BooleanField(
        default=False, blank=True,
        verbose_name='состояние ответа',
        help_text=(
            'Если ответ прочитан, '
            'отметьте галочкой'
        )
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.message


class Reminders(models.Model):
    TYPE_CHOICES = (
        (settings.FIRST_REMINDER_TYPE, 'Первое напоминание'),
        (settings.SECOND_REMINDER_TYPE, 'Второе напоминание'),
    )
    reminder_text = models.TextField(
        blank=False,
        verbose_name='Текст напоминания',
        help_text='Введите текст напоминания',
    )
    reminder_days = models.PositiveIntegerField(
        default=0,
        verbose_name='Интервал отправки в днях',
        help_text='Укажите через сколько дней отправлять напоминание',
    )
    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=30,
        unique=True,
        verbose_name='Тип напоминания',
        help_text='Выберите тип напоминания'
    )
    is_unsubscribe_button = models.BooleanField(
        default=False,
        verbose_name='Кнопка "Отписаться"',
        help_text='Показать кнопку "Отписатьсся"?'
    )

    class Meta:
        verbose_name = 'Напоминание'
        verbose_name_plural = 'Напоминания'
        ordering = ['reminder_days']

    def __str__(self):
        return f'{self.get_type_display()} - {self.id}'


@receiver(pre_save, sender=Reminders)
def set_default_reminder_days(sender, instance, **kwargs):
    if not instance.reminder_days or instance.reminder_days == 0:
        if instance.type == settings.FIRST_REMINDER_TYPE:
            instance.reminder_days = settings.FIRST_REMINDERS_DAYS
        elif instance.type == settings.SECOND_REMINDER_TYPE:
            instance.reminder_days = settings.SECOND_REMINDERS_DAYS


class Mailing_message(models.Model):
    message_type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=30,
        default='ПРОГРАММИРОВАНИЕ',
        verbose_name='тип сообщения',
        help_text='Введите тип сообщения'
    )
    message = models.TextField(
        verbose_name='Сообщение пользователей',
        help_text=(
            'Введите сообщение, '
            'которое надо отправить'
        )
    )
    sorted = models.IntegerField(
        verbose_name='Очередность сообщения',
        help_text=(
            'Введите номер, '
            'сообщения в очереди'
        )
    )

    class Meta:
        verbose_name = 'Сообщение для рассылки'
        verbose_name_plural = 'Сообщения для рассылки'
        ordering = ['message_type']

    def __str__(self):
        return 'Сообщения для рассылки'


class Mailing(models.Model):
    uservk = models.ForeignKey(
        UserVk,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    type_mailing = models.CharField(
        choices=TYPE_CHOICES,
        max_length=30,
        default='ПРОГРАММИРОВАНИЕ',
        verbose_name='тип рассылки',
        help_text='Введите тип рассылки'
    )
    counter = models.IntegerField(
        blank=True,
        default=0,
        verbose_name=('Количество отправленных сообщений')
    )
    messages = models.ManyToManyField(
        Mailing_message,
        verbose_name='Сообщение для рассылки',
        help_text='Выберите сообщения для рассылки'
    )
    is_activated = models.BooleanField(
        default=True,
        verbose_name='Подписка на рассылку',
        help_text=(
            'Показывает, подписан ли пользователь на  рассылку'
        ),
    )

    def unactivate(self):
        self.is_activated = False
        self.save()
        return

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return 'Рассылка'


class MailingMessageForAll(models.Model):
    message_text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Введите текст сообщения для рассылки'
    )

    class Meta:
        verbose_name = 'Сообщение для разовой рассылки'
        verbose_name_plural = 'Сообщения для разовой рассылки'

    def __str__(self):
        return self.message_text
