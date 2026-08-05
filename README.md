# AppStore — Django App Download Website

A simple, clean Django web app where an admin uploads Android APK and Windows EXE files, and visitors can browse and download them.

**Deploy on PythonAnywhere:** see [DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md).

## Features

### Storefront
- Mandatory sign-in (Google OAuth + manual form)
- Hero, live stats, rich cards, featured apps, recently viewed
- Search, sort (newest / downloads / name), platform & extra filters
- Detail: trust strip, changelog, requirements, screenshots, SHA-256
- Platform picker modal, sticky mobile download bar, share + report
- About / Privacy / Terms; branded 404 / 403 / 500 pages
- Light & dark mode, toasts, favicon, responsive UI

### Dashboard (staff)
- Stats, activity feed, bulk actions, CSV export
- Drag-and-drop APK / EXE / icon upload
- Draft vs published, featured & verified flags, screenshots
- Post-save success screen with “View in store”

### Technical
- Per-platform downloads, `.apk` / `.exe` validation
- Django admin still available at `/admin/`

## Tech Stack

| Layer     | Choice                          |
|-----------|---------------------------------|
| Backend   | Django (no DRF)                 |
| Frontend  | Django templates + Bootstrap 5  |
| Database  | SQLite                          |
| Storage   | Local `MEDIA_ROOT`              |
| Auth      | Manual form + Google OAuth (django-allauth) |

## Authentication (mandatory)

Everyone must sign in before browsing or downloading apps.

**Two sign-in methods on `/login/`:**

1. **Google OAuth** — “Continue with Google”
2. **Manual form** — username + password (or create an account at `/register/` by filling first name, last name, email, username, password)

| Role | Access |
|------|--------|
| Signed-in user | Storefront browse + download |
| Staff (`is_staff`) | Custom dashboard + uploads |
| Superuser | Django admin at `/admin/` as well |

### Enable Google OAuth

1. Create an OAuth client in [Google Cloud Console](https://console.cloud.google.com/)  
   - Type: **Web application**  
   - Authorized redirect URI:  
     `http://127.0.0.1:8000/accounts/google/login/callback/`
2. Set environment variables before starting the server:

```powershell
$env:GOOGLE_CLIENT_ID="your-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET="your-secret"
python manage.py runserver
```

Or create a **Social Application** in Django admin:  
**Social Applications → Add** → Provider `Google`, paste client id/secret, choose site `127.0.0.1:8000`.

Until credentials are set, the Google button stays disabled and manual login/register still works.

## Project Structure

```
.
├── config/                 # Django project settings & root URLs
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── store/                  # Main app
│   ├── models.py           # App model + file validators
│   ├── views.py            # home, detail, download
│   ├── admin.py
│   └── urls.py
├── templates/
│   ├── base.html
│   └── store/
│       ├── home.html
│       └── detail.html
├── media/                  # Uploaded files (created at runtime)
├── manage.py
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run migrations

```bash
python manage.py migrate
```

### 3. Create an admin user

```bash
python manage.py createsuperuser
```

### 4. Start the server

```bash
python manage.py runserver
```

### 5. Use the site

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/ | Homepage — browse apps |
| http://127.0.0.1:8000/app/&lt;id&gt;/ | App detail |
| http://127.0.0.1:8000/download/&lt;id&gt;/android/ | Download Android APK |
| http://127.0.0.1:8000/download/&lt;id&gt;/windows/ | Download Windows EXE |
| http://127.0.0.1:8000/dashboard/ | Custom management dashboard |
| http://127.0.0.1:8000/admin/ | Django default admin (optional) |

## Uploading Apps (custom dashboard)

1. Open http://127.0.0.1:8000/dashboard/
2. Sign in with a staff account (`admin` / `admin123` by default)
3. Click **Upload app**
4. Fill in name, description, version (and optional icon)
5. Upload **Android APK** and/or **Windows EXE**
6. At least one platform file is required
7. Save — the app appears on the storefront immediately

You can also edit or delete apps from the dashboard table.

## URLs

| Path | View |
|------|------|
| `/` | Home (list + search + platform filter) |
| `/app/<id>/` | App detail |
| `/download/<id>/android/` | Android download |
| `/download/<id>/windows/` | Windows download |
| `/dashboard/` | Custom management dashboard |
| `/dashboard/apps/new/` | Upload app |
| `/dashboard/apps/<id>/edit/` | Edit app |
| `/dashboard/apps/<id>/delete/` | Delete app |
| `/admin/` | Django admin (optional) |

## Notes

- Android files are stored under `media/apps/android/`
- Windows files are stored under `media/apps/windows/`
- Icons under `media/icons/`
- Max upload size is set to **200 MB** in settings
- Android field accepts **`.apk` only**; Windows field accepts **`.exe` only**
- Icons accept PNG, JPG, GIF, WEBP, SVG
