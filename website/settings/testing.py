import tempfile

from .base import *

DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

SECRET_KEY = os.environ.get("SECRET_KEY", "test-secret-key")

ALLOWED_HOSTS = ["*"]

SILENCED_SYSTEM_CHECKS = [
    "django_vite.W001",  # Silence missing Vite manifest warning
    "staticfiles.W004",  # Silence missing staticfiles directory warning
]

DJANGO_VITE = {
    "default": {
        "dev_mode": True,
    }
}

# Store files locally
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

TASKS["default"]["BACKEND"] = "django.tasks.backends.immediate.ImmediateBackend"

# Write uploaded/generated files (e.g. media.Image renditions) to a throwaway
# directory instead of the real MEDIA_ROOT, so test runs don't leave files behind.
MEDIA_ROOT = tempfile.mkdtemp(prefix="transakt_test_media_")

# Suppress log output during test runs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "CRITICAL"},
}

# Use a fast password hasher to speed up tests that create users
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
