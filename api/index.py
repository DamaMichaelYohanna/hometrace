"""Vercel entrypoint for the Hometrace Django application."""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hometrace_project.settings")

from hometrace_project.wsgi import application

# Cold-start safeguard: ensure database schema and initial data exist
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'properties_property'")
        table_exists = cursor.fetchone()
    if not table_exists:
        from django.core.management import call_command
        print("Vercel cold start: applying migrations...")
        call_command('migrate', interactive=False)
        print("Vercel cold start: seeding initial Keffi listings...")
        call_command('seed_data', if_empty=True, interactive=False)
except Exception as exc:
    print(f"Database schema check notice: {exc}")

app = application
