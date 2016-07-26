from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'get-asset-information': {
        'task': 'tasks.compile_asset_information',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (),
        },
    'get-vocabulary': {
        'task': 'tasks.compile_vocabulary',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (),
        },
    'get-streams': {
        'task': 'tasks.compile_streams',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (),
        },
    'get-large-format-files-every': {
        'task': 'tasks.compile_large_format_files',
        'schedule': crontab(minute=0, hour='*/12'),
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
        }
    }
