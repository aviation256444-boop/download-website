"""
Copy/adapt this into your PythonAnywhere Web → WSGI configuration file.

Replace YOUR_USERNAME and the project folder name if different.
"""

import os
import sys
from pathlib import Path

# --- Project path (adjust if your clone path differs) ---
project_home = '/home/YOUR_USERNAME/download-website'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# --- Virtualenv site-packages (adjust venv name if needed) ---
# Example after: mkvirtualenv --python=python3.10 appstore-env
# Or: path/to/venv/lib/python3.x/site-packages
venv_site = '/home/YOUR_USERNAME/.virtualenvs/appstore-env/lib/python3.10/site-packages'
if os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# --- Load .env then start Django ---
from dotenv import load_dotenv

load_dotenv(Path(project_home) / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
