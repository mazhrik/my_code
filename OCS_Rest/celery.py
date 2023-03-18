import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OCS_Rest.settings')
app = Celery('OCS_Rest')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     Calls test('hello') every 10 seconds.
#    sender.add_periodic_task(10, periodic_tasks, name='add every 10')

app.conf.beat_schedule = {
    # Executes at sunset in Melbourne
    'periodic': {
        'task': 'periodic_tasks',
        'schedule': 21600,
        # 'schedule': crontab(minute=0, hour='*/8'),
    },
}
