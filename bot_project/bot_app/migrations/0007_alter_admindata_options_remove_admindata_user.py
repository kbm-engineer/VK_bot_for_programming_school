# Generated by Django 4.2 on 2023-08-05 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0006_remove_uservk_phonenumber_uservk_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admindata',
            options={'verbose_name': 'Данные группы', 'verbose_name_plural': 'Данные групп'},
        ),
        migrations.RemoveField(
            model_name='admindata',
            name='user',
        ),
    ]
