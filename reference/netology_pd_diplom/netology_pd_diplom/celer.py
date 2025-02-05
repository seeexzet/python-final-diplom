import os
from celery import Celery

# Устанавливаем настройки Django (указываем правильный модуль настроек)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')

app = Celery('netology_pd_diplom')

# Загружаем настройки из Django settings с префиксом CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем задачи в установленных приложениях
app.autodiscover_tasks()
