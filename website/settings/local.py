import os

from .base import *

ENVIRONMENT = "LOCAL"
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

# Allow credentials for Session Auth with Vue dev server
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]

# Plain filenames locally; hashing needs collectstatic and only matters for caching in prod
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    },
}

# Django Vite settings
# https://github.com/MrBin99/django-vite?tab=readme-ov-file
DJANGO_VITE = {
    "default": {
        "dev_mode": True,
        "dev_server_port": 3000,
        "manifest_path": os.path.join(BASE_DIR, "assets/.vite/manifest.json"),
    },
}

ENABLE_ZEAL = os.environ.get("ENABLE_ZEAL", "False") == "True"
if ENABLE_ZEAL and not TESTING:
    INSTALLED_APPS.append("zeal")
    MIDDLEWARE.append("zeal.middleware.zeal_middleware")

# Django-zeal config
ZEAL_NPLUSONE_THRESHOLD = 3
ZEAL_RAISE = False
ZEAL_ALLOWLIST = [{"model": "contenttypes.ContentType"}]
ZEAL_SHOW_ALL_CALLERS = False  # Whether to show full call stack

if TESTING:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": "CRITICAL"},
    }

    # Keep tests off the dev Redis
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

    # Use a fast password hasher to speed up tests that create users
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
