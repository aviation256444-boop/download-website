"""
WSGI config for config project.

On PythonAnywhere the dashboard WSGI file should point at this module, or
copy the path-setup pattern from pythonanywhere_wsgi.py into the PA editor.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Ensure .env is loaded before Django settings (PythonAnywhere WSGI path)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
