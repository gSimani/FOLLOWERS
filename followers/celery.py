import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'followers.settings')

app = Celery('followers')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'cleanup-completed-tasks': {
        'task': 'social_automation.scheduler.cleanup_completed_tasks',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'retry-failed-tasks': {
        'task': 'social_automation.scheduler.retry_failed_tasks',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    },
    'update-analytics': {
        'task': 'social_automation.tasks.update_analytics',
        'schedule': crontab(hour='*/6'),  # Run every 6 hours
    },
    'process-schedules': {
        'task': 'social_automation.tasks.process_schedules',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
}

# Additional Celery settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3540,  # 59 minutes
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 