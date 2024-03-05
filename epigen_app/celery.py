import os

from celery import Celery
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epigen_app.settings.local')

app = Celery('epigen_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'remove_samples': {
        'task': 'remove_old_samples',
        'schedule': crontab(minute=0, hour=0),
        },
}

# Codigo para utilizar celery beat como cronjob
# app.conf.beat_schedule = {
#     #Scheduler Name
#     'pipeline-every-minute': {
#         # Task Name (Name Specified in Decorator)
#         'task': 'pipeline_cron',
#         # Schedule
#         'schedule': 60.0,
#     },
#     'send-report-every-minute': {
#         # Task Name (Name Specified in Decorator)
#         'task': 'send_email',
#         # Schedule
#         'schedule': 120.0,
#     },
#     'send-report-every-minute': {
#         # Task Name (Name Specified in Decorator)
#         'task': 'send_report',
#         # Schedule
#         'schedule': 30.0,
#     },
# }
