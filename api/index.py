"""Vercel entrypoint for the Hometrace Django application."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hometrace_project.settings")

from hometrace_project.wsgi import application

app = application
