from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "my.domain",
    ".my.domain",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ORIGINS = [
    "https://my.domain",
    "https://www.my.domain",
]

CSRF_TRUSTED_ORIGINS = [
    "https://my.domain",
    "https://*.my.domain",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "WARNING"},
}
