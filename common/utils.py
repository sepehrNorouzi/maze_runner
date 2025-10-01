from django.conf import settings

def run_lazy(func, *args, **kwargs):
    celery_availability = getattr(settings, 'USE_CELERY') or False
    if not celery_availability:
        func(*args, **kwargs)
    func.delay(*args, **kwargs)
