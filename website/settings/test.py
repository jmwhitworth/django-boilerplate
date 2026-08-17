import tempfile

from .base import *

DEBUG = True

TASKS["default"]["BACKEND"] = "django.tasks.backends.immediate.ImmediateBackend"

# Use local media storage and non-whitenoise static files storage for testing
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Write uploaded/generated files (e.g. media.Image renditions) to a throwaway
# directory instead of the real MEDIA_ROOT, so test runs don't leave files behind.
MEDIA_ROOT = tempfile.mkdtemp(prefix="transakt_test_media_")

# Suppress log output during test runs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "CRITICAL"},
}
