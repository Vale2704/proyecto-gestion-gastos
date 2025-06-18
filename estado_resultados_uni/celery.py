import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estado_resultados_uni.settings')
 
app = Celery('estado_resultados_uni')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 