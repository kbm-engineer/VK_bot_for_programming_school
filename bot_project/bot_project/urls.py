from django.contrib import admin
from django.urls import path

from bot_app.views import vk_callback


urlpatterns = [
    path('admin/', admin.site.urls),
    path('vk_callback/', vk_callback, name='vk_callback'),
]
