"""
config/settings/base.py
Konfigurasi Django dasar yang dipakai oleh dev.py dan prod.py.
Semua nilai sensitif dibaca dari .env menggunakan django-environ.
"""

from pathlib import Path
import environ

# ─── Base Directory ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── Environment ──────────────────────────────────────────────────────────────
env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# ─── Core Django ──────────────────────────────────────────────────────────────
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-ganti-di-production-wajib!")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ─── Installed Apps ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django minimal (tidak pakai admin bawaan, auth Django, atau sessions)
    "django.contrib.contenttypes",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local apps (feature-based)
    "core",
    "accounts",
    "berita",
    "profil",
    "proker",
    "pengaduan",
    "storage_files",
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",         # wajib paling atas
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─── Database ─────────────────────────────────────────────────────────────────
# SQLite minimal — hanya untuk kebutuhan internal Django jika ada.
# DATA BISNIS (berita, profil, proker, pengaduan) disimpan di Firestore.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Localization ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = "id-ID"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.authentication.FirebaseAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"]
)
CORS_ALLOW_CREDENTIALS = True

# ─── Firebase (Auth + Firestore saja, Storage sudah diganti Cloudinary) ──────
FIREBASE_SERVICE_ACCOUNT_PATH = env(
    "FIREBASE_SERVICE_ACCOUNT_PATH", default="firebase-service-account.json"
)

# ─── Cloudinary (File Storage) ────────────────────────────────────────────────
# Kredensial didapat dari: cloudinary.com → Dashboard → API Keys
CLOUDINARY_CLOUD_NAME = env("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = env("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = env("CLOUDINARY_API_SECRET", default="")

# Pilihan pengiriman URL: True = selalu pakai https://res.cloudinary.com (CDN)
CLOUDINARY_SECURE = env.bool("CLOUDINARY_SECURE", default=True)

# ─── Email (SMTP) ─────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@ipmjabar.or.id")
ADMIN_NOTIF_EMAIL = env("ADMIN_NOTIF_EMAIL", default="admin@ipmjabar.or.id")
