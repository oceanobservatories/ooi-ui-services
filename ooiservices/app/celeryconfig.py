from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'get-assets': {
        'task': 'tasks.compile_assets',
        'schedule': crontab(minute='*/10'),
        'args': (),
        },
    'get-streams': {
        'task': 'tasks.compile_streams',
        'schedule': crontab(minute='*/3'),
        'args': (),
        },
    'get-events': {
        'task': 'tasks.compile_events',
        'schedule': crontab(minute='*/5'),
        'args': (),
        },
    'get-glider-traks-every': {
        'task': 'tasks.compile_glider_tracks',
        'schedule': crontab(hour='*/8'),
        'args': (),
        },
    }
