# app/celery_app/celery_instance.py
from celery import Celery
from app.celery_app.config import CELERY_CONFIG

app = Celery("tasks")
app.config_from_object(CELERY_CONFIG)
