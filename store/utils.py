from datetime import timedelta

from django.db.models import F, Q
from django.utils import timezone

from .models import App


def published_apps():
    return App.objects.filter(is_published=True)


def apply_app_filters(qs, request):
    """Apply search, platform, sort, and extra filters from GET params."""
    query = request.GET.get('q', '').strip()
    platform = request.GET.get('platform', '').strip().lower()
    sort = request.GET.get('sort', 'newest').strip().lower()
    has_icon = request.GET.get('has_icon', '') == '1'
    updated_month = request.GET.get('updated', '') == 'month'

    if query:
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(version__icontains=query)
            | Q(changelog__icontains=query)
        )

    if platform == 'android':
        qs = qs.exclude(android_file='').exclude(android_file__isnull=True)
    elif platform == 'windows':
        qs = qs.exclude(windows_file='').exclude(windows_file__isnull=True)

    if has_icon:
        qs = qs.exclude(icon='').exclude(icon__isnull=True)

    if updated_month:
        since = timezone.now() - timedelta(days=30)
        qs = qs.filter(updated_at__gte=since)

    if sort == 'downloads':
        qs = qs.annotate(
            total_dl=F('android_download_count') + F('windows_download_count')
        ).order_by('-is_featured', '-total_dl', '-created_at')
    elif sort == 'name':
        qs = qs.order_by('-is_featured', 'name')
    else:  # newest
        qs = qs.order_by('-is_featured', '-created_at')

    return qs, {
        'query': query,
        'platform': platform if platform in ('android', 'windows') else '',
        'sort': sort if sort in ('newest', 'downloads', 'name') else 'newest',
        'has_icon': has_icon,
        'updated_month': updated_month,
    }


def track_recently_viewed(request, app_id, limit=8):
    """Store recently viewed app IDs in the session."""
    key = 'recently_viewed'
    ids = request.session.get(key, [])
    app_id = int(app_id)
    ids = [i for i in ids if i != app_id]
    ids.insert(0, app_id)
    request.session[key] = ids[:limit]
    request.session.modified = True
    return request.session[key]


def get_recently_viewed_apps(request, exclude_id=None, limit=6):
    ids = request.session.get('recently_viewed', [])
    if exclude_id:
        ids = [i for i in ids if i != int(exclude_id)]
    if not ids:
        return App.objects.none()
    apps = list(published_apps().filter(pk__in=ids[:limit]))
    order = {pk: idx for idx, pk in enumerate(ids)}
    apps.sort(key=lambda a: order.get(a.pk, 999))
    return apps
