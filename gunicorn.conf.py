import os

# Fixed default rather than cpu_count(), which reports the host's cores inside a container
workers = int(os.environ.get("GUNICORN_WORKERS") or 4)
