import os

from pathlib import Path
from dotenv import load_dotenv

from bot_app.utils import force_int

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_KEY', default='default_key')

_TRUE_STRINGS = ['1', 'True', 'true']

DEBUG = os.getenv('APP_IS_DEBUG') in _TRUE_STRINGS

ALLOWED_HOSTS = tuple((os.getenv('APP_ALLOWED_HOSTS') or '*').split(','))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'bot_app.apps.Bot_appConfig',

    # Other apps
    "phonenumber_field",
    'import_export',
    'django_object_actions',

    # Celery apps
    'celery',
    'django_celery_results',
    'django_celery_beat',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bot_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bot_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME', default='postgres'),
            'USER': os.getenv('POSTGRES_USER', default='postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
            'HOST': os.getenv('DB_HOST', default='127.0.0.1'),
            'PORT': os.getenv('DB_PORT', default='5432')
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'ru-Ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

DATE_INPUT_FORMATS = ['%d-%m-%Y']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Настроки логгирования
LOG_SETTINGS = {
    'when': 'D',       # Ротация каждый день
    'interval': 1,
    'backupCount': 14  # Храним логи до двух недель
}

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = force_int(os.getenv('REDIS_PORT', 6379))

# Настройки Celery
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/9'  # URL для подключения к Redis
CELERY_RESULT_BACKEND = 'django-db'  # Бэкенд для хранения результатов задач Celery
CELERY_CACHE_BACKEND = 'default'  # Либо 'django-cache'

# Настройки VK-bot
VK = {
    'VK_API_TOKEN': os.getenv('VK_API_TOKEN'),
    'GROUP_ID': os.getenv('VK_API_GROUP_ID'),
    'QUIZ_RESPONSE_INTERVAL': force_int(os.getenv('VK_API_QUIZ_RESPONSE_INTERVAL')),
    'TASKS_INTERVAL': force_int(os.getenv('VK_API_TASKS_INTERVAL'))
}

# Настройки напоминаний
REMINDERS_INTERVAL_HOURS = 3
FIRST_REMINDERS_DAYS = 1
SECOND_REMINDERS_DAYS = 7
FIRST_REMINDER_TYPE = 'first_reminder'
SECOND_REMINDER_TYPE = 'second_reminder'
