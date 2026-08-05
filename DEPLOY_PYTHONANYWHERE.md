# Deploy AppStore on PythonAnywhere

**Your site:** https://download245.pythonanywhere.com  
**PA username:** `download245`  
**Repo:** https://github.com/aviation256444-boop/download-website

---

## 1. Clone the code

On PythonAnywhere **Bash** console:

```bash
cd ~
git clone https://github.com/aviation256444-boop/download-website.git
cd download-website
```

---

## 2. Create a virtualenv and install deps

```bash
# Free accounts often have Python 3.10 available — pick one that exists:
mkvirtualenv --python=/usr/bin/python3.10 appstore-env
# If mkvirtualenv is missing:
# python3.10 -m venv ~/.virtualenvs/appstore-env
# source ~/.virtualenvs/appstore-env/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Environment file on the server

```bash
cd ~/download-website
nano .env
```

Paste (edit secrets):

```env
DJANGO_SECRET_KEY=generate-a-long-random-string
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=download245.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://download245.pythonanywhere.com

GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4. Migrate, static files, superuser

```bash
cd ~/download-website
source ~/.virtualenvs/appstore-env/bin/activate   # if not already
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Update the Django **Sites** domain (required for allauth/Google):

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
s = Site.objects.get(id=1)
s.domain = 'download245.pythonanywhere.com'
s.name = 'AppStore'
s.save()
exit()
```

---

## 5. Web app configuration (Dashboard)

1. **Web** → **Add a new web app** → domain `download245.pythonanywhere.com` → **Manual configuration** → Python 3.10 (match venv).
2. **Source code**: `/home/download245/download-website`
3. **Working directory**: `/home/download245/download-website`
4. **Virtualenv**: `/home/download245/.virtualenvs/appstore-env`
5. **WSGI file**: open the WSGI configuration file link and **delete everything**, then paste the code below.
6. **Static files** mappings:

| URL        | Directory                                           |
|------------|-----------------------------------------------------|
| `/static/` | `/home/download245/download-website/staticfiles`    |
| `/media/`  | `/home/download245/download-website/media`          |

7. Click **Reload** on the Web tab.

### WSGI file (paste into PythonAnywhere)

Open **Web → WSGI configuration file** and replace the entire file with:

```python
"""
PythonAnywhere WSGI for download245.pythonanywhere.com
Paste this whole file into: Web → WSGI configuration file
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
# If Python version differs, fix the 3.10 path:
#   ls ~/.virtualenvs/appstore-env/lib/
venv_site = '/home/download245/.virtualenvs/appstore-env/lib/python3.10/site-packages'
if os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# --- Load .env then start Django ---
from dotenv import load_dotenv

load_dotenv(Path(project_home) / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

If the site-packages path is wrong (ImportError for Django), run this **inside the virtualenv** and update `venv_site` above:

```bash
workon appstore-env
python -c "import site; print(site.getsitepackages())"
```

---

## 6. Google OAuth on production

In [Google Cloud Console](https://console.cloud.google.com/) → OAuth client:

**Authorized JavaScript origins**
```text
https://download245.pythonanywhere.com
```

**Authorized redirect URIs**
```text
https://download245.pythonanywhere.com/accounts/google/login/callback/
```

Keep localhost entries if you still develop locally.

---

## 7. Upload size limits (important)

- Free PythonAnywhere accounts have **smaller HTTP request body limits** than the app’s 200 MB setting.
- Large APK/EXE uploads may need a **paid** plan or uploading via the Files tab + admin path adjustments.
- Icons and small builds usually work fine.

---

## 8. Updating after code changes

```bash
cd ~/download-website
source ~/.virtualenvs/appstore-env/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Web → Reload**.

---

## Checklist

- [ ] `.env` on server with `DJANGO_DEBUG=0` and host `download245.pythonanywhere.com`
- [ ] `migrate` + `collectstatic` + superuser
- [ ] Site domain = `download245.pythonanywhere.com`
- [ ] WSGI paths + virtualenv correct
- [ ] Static `/static/` → `staticfiles`, Media `/media/` → `media`
- [ ] Google redirect URI = `https://download245.pythonanywhere.com/accounts/google/login/callback/`
- [ ] Web app reloaded

Open: **https://download245.pythonanywhere.com/**
