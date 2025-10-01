import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maze_runner.settings")
app = Celery("maze_runner")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
