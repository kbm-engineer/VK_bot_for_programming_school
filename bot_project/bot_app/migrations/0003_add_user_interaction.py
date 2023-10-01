# Generated by Django 4.2 on 2023-08-03 20:19

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0002_admindata_mailing_message_and_mailing_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uservk',
            name='is_first_reminder_sent',
        ),
        migrations.RemoveField(
            model_name='uservk',
            name='is_second_reminder_sent',
        ),
        migrations.RemoveField(
            model_name='uservk',
            name='last_interaction',
        ),
        migrations.AlterField(
            model_name='message',
            name='uservk',
            field=models.ForeignKey(default=None, help_text='Выберите пользователя', on_delete=django.db.models.deletion.CASCADE, to='bot_app.uservk', verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='uservk',
            name='phoneNumber',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='Введите Ваш телефонный номер', max_length=128, region=None, verbose_name='Телефонный номер'),
        ),
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_interaction', models.DateTimeField(default=django.utils.timezone.now, help_text='Показывает, когда пользователь взаимодействовал с ботом первый раз', verbose_name='Дата первого взаимодействия')),
                ('last_interaction', models.DateTimeField(default=django.utils.timezone.now, help_text='Показывает, когда пользователь взаимодействовал с ботом последний раз', verbose_name='Дата последнего взаимодействия')),
                ('is_first_reminder_sent', models.BooleanField(default=False, help_text='Показывает, было ли отправлено первое напоминание', verbose_name='Первое напоминание отправлено')),
                ('is_second_reminder_sent', models.BooleanField(default=False, help_text='Показывает, было ли отправлено второе напоминание', verbose_name='Второе напоминание отправлено')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='bot_app.uservk', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Взаимодействие с ботом',
                'verbose_name_plural': 'Взаимодействия с ботом',
            },
        ),
    ]