# Deploy AppStore on PythonAnywhere

This guide assumes a **Beginner (free)** or paid PythonAnywhere account and a clone of this GitHub repo.

---

## 1. Push / clone the code

On PythonAnywhere **Bash** console:

```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USER/download-website.git
cd download-website
```

(Use the real repo URL after push.)

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

Paste (edit values):

```env
DJANGO_SECRET_KEY=generate-a-long-random-string
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com

GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

Generate a secret key locally or in the console:

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
s.domain = 'YOUR_USERNAME.pythonanywhere.com'
s.name = 'AppStore'
s.save()
exit()
```

---

## 5. Web app configuration (Dashboard)

1. **Web** → **Add a new web app** → **Manual configuration** → Python 3.10 (match venv).
2. **Source code**: `/home/YOUR_USERNAME/download-website`
3. **Working directory**: `/home/YOUR_USERNAME/download-website`
4. **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/appstore-env`
5. **WSGI file**: open the link and **replace** the file contents with the adapted version of `pythonanywhere_wsgi.py` from this repo:
   - Set `project_home` to `/home/YOUR_USERNAME/download-website`
   - Set `venv_site` to your real `site-packages` path (check with `python -c "import site; print(site.getsitepackages())"` inside the venv)
6. **Static files** mappings:

| URL        | Directory                                      |
|------------|------------------------------------------------|
| `/static/` | `/home/YOUR_USERNAME/download-website/staticfiles` |
| `/media/`  | `/home/YOUR_USERNAME/download-website/media`   |

7. Click **Reload** on the Web tab.

---

## 6. Google OAuth on production

In [Google Cloud Console](https://console.cloud.google.com/) → OAuth client:

**Authorized JavaScript origins**
```text
https://YOUR_USERNAME.pythonanywhere.com
```

**Authorized redirect URIs**
```text
https://YOUR_USERNAME.pythonanywhere.com/accounts/google/login/callback/
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

- [ ] `.env` on server with `DJANGO_DEBUG=0` and correct host
- [ ] `migrate` + `collectstatic` + superuser
- [ ] Site domain = `YOUR_USERNAME.pythonanywhere.com`
- [ ] WSGI paths + virtualenv correct
- [ ] Static `/static/` → `staticfiles`, Media `/media/` → `media`
- [ ] Google redirect URI uses `https://…pythonanywhere.com/...`
- [ ] Web app reloaded

Open: `https://YOUR_USERNAME.pythonanywhere.com/`
