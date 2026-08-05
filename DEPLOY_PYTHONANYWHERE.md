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
5. **WSGI file**: open the link and **replace** contents with `pythonanywhere_wsgi.py` from the repo (already set for `download245`).
   - If site-packages path fails, check:  
     `python -c "import site; print(site.getsitepackages())"` inside the venv
6. **Static files** mappings:

| URL        | Directory                                           |
|------------|-----------------------------------------------------|
| `/static/` | `/home/download245/download-website/staticfiles`    |
| `/media/`  | `/home/download245/download-website/media`          |

7. Click **Reload** on the Web tab.

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
