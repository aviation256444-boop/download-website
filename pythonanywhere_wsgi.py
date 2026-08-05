"""
Copy this into your PythonAnywhere Web → WSGI configuration file
(or use as reference). Paths are for user: download245
"""

import os
import sys
from pathlib import Path

# --- Project path ---
project_home = '/home/download245/download-website'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# --- Virtualenv site-packages ---
# After: mkvirtualenv --python=python3.10 appstore-env
# If Python version differs, fix the 3.10 path (ls ~/.virtualenvs/appstore-env/lib/)
venv_site = '/home/download245/.virtualenvs/appstore-env/lib/python3.10/site-packages'
if os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# --- Load .env then start Django ---
from dotenv import load_dotenv

load_dotenv(Path(project_home) / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
