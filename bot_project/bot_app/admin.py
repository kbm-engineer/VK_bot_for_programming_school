from django.conf import settings
from django.contrib import admin
from django_celery_beat.admin import PeriodicTaskAdmin
from django_celery_beat.models import (
    ClockedSchedule, CrontabSchedule,
    IntervalSchedule, PeriodicTask,
    SolarSchedule
)
from django.http import HttpResponseRedirect
from django_object_actions import DjangoObjectActions
from import_export.admin import ImportExportModelAdmin

from bot_app.message_sender import MyBot
from bot_app.models import (
    AdminData, Mailing, Mailing_message, MailingMessageForAll, Message,
    MessageCourses, Reminders, UserInteraction, UserVk
)

from bot_app.utils import export_xls


conf = settings.VK


@admin.register(UserVk)
class UserVkAdmin(DjangoObjectActions, ImportExportModelAdmin):
    list_display = (
        'user_id', 'first_name',
        'last_name', 'city',
        'phone_number', 'is_subscribed'
    )
    search_fields = ('last_name',)
    list_filter = ('is_subscribed', 'city')

    def static(modeladmin, request, queryset):
        return export_xls()

    def send_message_view(self, request, queryset):
        #TODO: переделать на кнопку
        try:
            message = MailingMessageForAll.objects.get()
        except:
            self.message_user(
                request,
                'У вас отсутствуют сообщение в Модели "Сообщения для разовой рассылки".',
                level='ERROR')
            return HttpResponseRedirect(request.get_full_path())
        bot = MyBot(token=conf.get('VK_API_TOKEN'), group_id=conf.get('GROUP_ID'))

        for user in queryset:
            bot.send_message(user_id=user.user_id, message=message)

        self.message_user(
            request,
            f'Сообщение успешно отправлено {queryset.count()} пользователям.',
            level='SUCCESS'
        )
        return HttpResponseRedirect(request.get_full_path())

    changelist_actions = ('static',)
    actions = ('send_message_view',)
    send_message_view.short_description = 'Отправить сообщение выбранным пользователям'


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'first_interaction', 'last_interaction',
        'is_first_reminder_sent', 'is_second_reminder_sent'
    )
    list_filter = (
        'is_first_reminder_sent',
        'is_second_reminder_sent'
    )
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__user_id'
    )


@admin.register(AdminData)
class AdminDataAdmin(admin.ModelAdmin):
    list_display = (
        'admin_id', 'is_active'
    )
    search_fields = (
        'admin_id',
    )


@admin.register(MessageCourses)
class MessageCoursesAdmin(admin.ModelAdmin):
    list_display = (
        'message', 'is_active'
    )
    search_fields = (
        'message',
    )


@admin.register(Message)
class MessagekAdmin(ImportExportModelAdmin):
    list_display = (
        'uservk', 'message_type',
        'message', 'vk_time',
        'answered',
    )


@admin.register(Reminders)
class RemindersAdmin(admin.ModelAdmin):

    def short_reminder_text(self, obj):
        max_length = 20
        if len(obj.reminder_text) <= max_length:
            return obj.reminder_text
        return f'{obj.reminder_text[:max_length]}...'
    short_reminder_text.short_description = 'Текст напоминания'

    list_display = (
        'get_type_display',
        'short_reminder_text',
        'reminder_days',
        'is_unsubscribe_button'
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('uservk', 'counter', 'type_mailing', 'is_activated')


@admin.register(MailingMessageForAll)
class MailingMessageForAllAdmin(admin.ModelAdmin):
    list_display = ('message_text',)


@admin.register(Mailing_message)
class MailingMessageAdmin(ImportExportModelAdmin):
    list_display = ('message_type', 'message', 'sorted')


# Отменяем регистрацию существующего приложения PeriodicTask
admin.site.unregister(PeriodicTask)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)


class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    pass
