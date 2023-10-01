import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from bot_app.message_sender import MyBot
from bot_app.tasks import export_users_xls


conf = settings.VK

def user_statistic(request):
    filename = "statics.txt"
    content = export_users_xls.delay().get()
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@csrf_exempt
def vk_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        SECRET_KEY = conf.get('SECRET_KEY')
        TOKEN = conf.get('VK_API_TOKEN')
        if data['type'] == 'confirmation':
            return HttpResponse(SECRET_KEY, content_type='text/plain', status=200)

        elif data['type'] == 'message_new':
            MyBot(token=TOKEN).message_handler(data)
            return HttpResponse('OK', content_type='text/plain', status=200)
    return HttpResponse('Invalid request method', content_type='text/plain', status=400)
