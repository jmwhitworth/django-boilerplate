import os

from .base import *

ENVIRONMENT = "STAGING"
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = []

INTERNAL_IPS = []
