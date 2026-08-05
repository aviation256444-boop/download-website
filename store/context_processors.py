from .models import SiteSettings


def site_extras(request):
    """Global template context: branding, support email, app version."""
    try:
        settings_obj = SiteSettings.load()
    except Exception:
        settings_obj = None
    return {
        'site_settings': settings_obj,
        'app_version': '1.2.0',
        'support_email': (
            settings_obj.support_email if settings_obj else 'support@appstore.local'
        ),
    }
