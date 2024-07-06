import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alphafrog.settings')

app = Celery('alphafrog')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 显式包含任务模块
task_modules = [
    'domestic.tasks.index_tasks',
    'domestic.tasks.stock_tasks',
    'domestic.tasks.fund_tasks',
    'alpharecord.tasks.create_record_tasks',
]

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: task_modules, related_name=None)