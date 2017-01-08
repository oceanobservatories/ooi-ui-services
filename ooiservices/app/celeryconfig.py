from celery.schedules import crontab
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'US/Eastern'
CELERYBEAT_SCHEDULE = {
    'get-large-format-files-every': {
        'task': 'tasks.compile_large_format_files',
        'schedule': crontab(minute=0, hour=23),
        'args': (),
        },
    'get-cam-images-every': {
        'task': 'tasks.compile_cam_images',
        'schedule': crontab(minute=15, hour=2),
        'args': (),
        },
    'get-c2-toc': {
        'task': 'tasks.compile_c2_toc',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-toc-rds': {
        'task': 'tasks.compile_toc_rds',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-streams': {
        'task': 'tasks.compile_streams',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-vocabulary': {
        'task': 'tasks.compile_vocabulary',
        'schedule': crontab(minute=15, hour=1),
        'args': (),
        },
    'get-uid_digests': {
        'task': 'tasks.compile_uid_digests',
        'schedule': crontab(minute=30, hour=1),
        'args': (),
        },
    'get-asset-information': {
        'task': 'tasks.compile_asset_information',
        'schedule': crontab(minute=30, hour=4),
        'args': (),
        },
    }