from celery.schedules import crontab

CELERY_CONFIG = {
    "broker_url": "redis://redis:6379/1",
    "result_backend": "redis://redis:6379/1",
    "beat_schedule": {
        "print_message": {
            "task": "app.celery_app.tasks.user_tasks.broadcast_message",
            "schedule": 10.0,  # Execute every 10 seconds
        },
    },
}
