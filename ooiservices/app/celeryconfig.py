from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
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
