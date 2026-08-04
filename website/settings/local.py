import os

from .base import *

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

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "ENQUEUE_ON_COMMIT": False,
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
