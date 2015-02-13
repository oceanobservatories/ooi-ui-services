web: gunicorn ooiservices.manage:app
worker: celery worker --app=ooiservices.app.celery -E