"""
config/settings/prod.py
Konfigurasi untuk environment production (VPS Niagahoster/IDCloudHost).
Gunakan: DJANGO_SETTINGS_MODULE=config.settings.prod
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# ─── Security Headers ─────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS = 31_536_000          # 1 tahun
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# ─── Static Files ─────────────────────────────────────────────────────────────
# React Build di-serve langsung oleh Nginx, bukan Django
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
