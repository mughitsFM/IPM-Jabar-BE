"""
config/wsgi.py
WSGI config for backend project.
Dijalankan oleh Gunicorn di production:
  gunicorn config.wsgi:application --bind 0.0.0.0:8000
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
application = get_wsgi_application()
