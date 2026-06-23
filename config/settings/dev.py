"""
config/settings/dev.py
Konfigurasi untuk environment development lokal.
Gunakan: DJANGO_SETTINGS_MODULE=config.settings.dev
"""

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# CORS bebas di dev (tidak perlu whitelist origin)
CORS_ALLOW_ALL_ORIGINS = True

# Email: tampilkan di console saja, tidak kirim sungguhan
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Throttle lebih longgar di dev agar tidak menghambat testing
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/hour",
    "user": "10000/hour",
}
