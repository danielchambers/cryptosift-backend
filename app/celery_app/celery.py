# app/celery_app/celery.py
from app.celery_app.celery_instance import app
from app.celery_app.tasks import user_tasks

app.autodiscover_tasks(["app.celery_app.tasks"])