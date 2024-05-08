# app/celery_app/celery.py
from app.celery_app.celery_instance import app

app.autodiscover_tasks(["app.celery_app.tasks"])
