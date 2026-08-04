import os

from .base import *

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = []

INTERNAL_IPS = []
