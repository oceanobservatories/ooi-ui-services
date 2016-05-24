from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'get-assets-rd': {
        'task': 'tasks.compile_asset_rds',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-assets': {
        'task': 'tasks.compile_assets',
        'schedule': crontab(minute=0, hour='*/2'),
        'args': (),
        },
    'get-bad-assets': {
        'task': 'tasks.compile_bad_assets',
        'schedule': crontab(minute=0, hour='*/2'),
        'args': (),
        },
    'get-streams': {
        'task': 'tasks.compile_streams',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-events': {
        'task': 'tasks.compile_events',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-glider-traks-every': {
        'task': 'tasks.compile_glider_tracks',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (),
        },
    'get-cam-images-every': {
        'task': 'tasks.compile_cam_images',
        'schedule': crontab(minute=0, hour='*/12'),
        'args': (),
        },
    'get-c2-toc': {
        'task': 'tasks.compile_c2_toc',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    }
