from celery.schedules import crontab

CELERY_CONFIG = {
    "broker_url": "redis://redis:6379/1",
    "result_backend": "redis://redis:6379/1",
    "beat_schedule": {
        "news_message": {
            "task": "app.celery_app.tasks.news_tasks.broadcast_news_data",
            "schedule": crontab(minute="*/25"),
        },
        "discord_message": {
            "task": "app.celery_app.tasks.discord_tasks.broadcast_discord_data",
            "schedule": crontab(minute="*/15"),
        },
        "youtube_message": {
            "task": "app.celery_app.tasks.youtube_tasks.broadcast_youtube_data",
            "schedule": crontab(minute="*/30"),
        },
    },
}
