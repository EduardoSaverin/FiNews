import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

if load_dotenv():
    print("✅ .env loaded")

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

REDIS_URL = (
    f"redis://default:{REDIS_PASSWORD}"
    "@redis-19992.crce220.us-east-1-4.ec2.redns.redis-cloud.com:19992"
)

app = Celery(
    "finews",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.celery_tasks"]
)

app.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    beat_schedule={
        "fetch-articles-every-10-min": {
            "task": "app.tasks.celery_tasks.fetch_and_process_articles",
            "schedule": crontab(minute="*/10"),  # every 10 minutes
        },
    },
)