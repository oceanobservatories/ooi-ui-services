from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'tasks.compile_assets',
        'schedule': crontab(minute='*/5'),
        'args': (),
        },
    }
