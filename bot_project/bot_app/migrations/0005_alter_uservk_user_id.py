# Generated by Django 4.2 on 2023-08-04 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0004_uservk_is_subscribed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uservk',
            name='user_id',
            field=models.IntegerField(help_text='Введите индентификатор пользователя', unique=True, verbose_name='VK id'),
        ),
    ]
