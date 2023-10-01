from datetime import datetime

import concurrent.futures as pool
import xlwt
from django.db.models import Count
from django.http import HttpResponse
from functools import wraps


def force_int(value, default=0):
    '''
    Безопасное приведение к int
    '''
    try:
        return int(value)
    except:
        return default

def get_user_data(user_data):
    try:
        birthday_obj = datetime.strptime(user_data.get('bdate', None), '%d.%m.%Y').strftime('%Y-%m-%d')
    except Exception:
        birthday_obj = None
    user_id = user_data.get('id', None)
    if user_id:
        return{
            'user_id': user_data.get('id', None),
            'first_name' : user_data.get('first_name', None),
            'last_name': user_data.get('last_name', None),
            'city': user_data['city']['title'] if 'city' in user_data and 'title' in user_data['city'] else None,
            'birthday': birthday_obj,
            'phone_number': user_data.get('mobile_phone', None)
        }
    return

_DEFAULT_POOL = pool.ThreadPoolExecutor()

def threadpool(f, executor=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        return (executor or _DEFAULT_POOL).submit(f, *args, **kwargs)

    return wrap

@threadpool
def static_count_message():
    from bot_app.models import Message

    a = Message.objects.values_list(
        'uservk__last_name', 'uservk__first_name', 'uservk__user_id',
    ).annotate(Count('message'))
    b = Message.objects.values_list(
        'uservk__last_name', 'uservk__first_name', 'uservk__user_id', 'message'
    ).order_by('message_type')
    return [a, b]

def export_xls():
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    def xls(columns, rows, name):
        ws = wb.add_sheet(name)
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
    t = static_count_message()
    result = t.result()
    columns1 = ['last_name', 'first_name', 'vk_id', 'count_message']
    columns2 = ['last_name', 'first_name', 'vk_id', 'message']
    rows1 = result[0]
    rows2 = result[1]
    xls(columns1, rows1, 'count_message')
    xls(columns2, rows2, 'message_type')
    wb.save(response)
    return response

def get_group_admins_id():
    from bot_app.models import AdminData

    admins_id = []
    try:
        admins = AdminData.objects.filter(is_active=True).all()
        for admin in admins:
            admins_id.append(admin.admin_id)
    except Exception:
        pass
    return admins_id


def get_corse_message():
    from bot_app.models import MessageCourses

    message = ''
    try:
        message = MessageCourses.objects.filter(is_active=True).first()
        message = message.message
    except Exception:
        pass
    return message
