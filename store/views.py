import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import ReportForm
from .models import ActivityLog, App
from .utils import (
    apply_app_filters,
    get_recently_viewed_apps,
    published_apps,
    track_recently_viewed,
)

VALID_PLATFORMS = {'android', 'windows'}


@login_required
@require_GET
def home(request):
    """Homepage: featured apps, filters, sort, stats."""
    base = published_apps()
    apps, filters = apply_app_filters(base, request)

    featured = published_apps().filter(is_featured=True)[:6]
    # If filtering/searching, don't duplicate featured as a separate strip unless empty filters
    show_featured = (
        featured.exists()
        and not filters['query']
        and not filters['platform']
        and not filters['has_icon']
        and not filters['updated_month']
    )

    totals = published_apps().aggregate(
        android_downloads=Sum('android_download_count'),
        windows_downloads=Sum('windows_download_count'),
        app_total=Count('id'),
    )
    total_downloads = (totals['android_downloads'] or 0) + (totals['windows_downloads'] or 0)

    recently_viewed = get_recently_viewed_apps(request)

    return render(request, 'store/home.html', {
        'apps': apps,
        'app_count': apps.count(),
        'featured_apps': featured if show_featured else [],
        'show_featured': show_featured,
        'recently_viewed': recently_viewed,
        'store_stats': {
            'apps': totals['app_total'] or 0,
            'downloads': total_downloads,
        },
        **filters,
    })


@login_required
@require_GET
def app_detail(request, pk):
    """App detail with gallery, trust strip, share, report."""
    app = get_object_or_404(published_apps().prefetch_related('screenshots'), pk=pk)
    track_recently_viewed(request, app.pk)
    recently_viewed = get_recently_viewed_apps(request, exclude_id=app.pk)
    report_form = ReportForm()
    return render(request, 'store/detail.html', {
        'app': app,
        'recently_viewed': recently_viewed,
        'report_form': report_form,
        'download_started': request.GET.get('downloaded') == '1',
        'download_platform': request.GET.get('platform', ''),
    })


@login_required
@require_GET
def download_app(request, pk, platform):
    """Increment platform download count and serve that platform's file."""
    platform = (platform or '').lower()
    if platform not in VALID_PLATFORMS:
        raise Http404('Unknown platform.')

    app = get_object_or_404(published_apps(), pk=pk)
    file_field = app.get_file_for_platform(platform)

    if not file_field:
        raise Http404(f'No {platform.title()} file available for this app.')

    count_field = (
        'android_download_count' if platform == 'android' else 'windows_download_count'
    )
    App.objects.filter(pk=pk).update(**{count_field: F(count_field) + 1})

    ActivityLog.log(
        user=request.user,
        app=app,
        action=ActivityLog.ACTION_DOWNLOAD,
        message=f'{request.user.username} downloaded {app.name} ({platform})',
    )

    try:
        response = FileResponse(
            file_field.open('rb'),
            as_attachment=True,
            filename=file_field.name.split('/')[-1],
        )
        return response
    except FileNotFoundError:
        raise Http404('File not found on disk.')


@login_required
@require_http_methods(['GET', 'POST'])
def report_app(request, pk):
    """Simple report-a-problem form (logs + flashes support email)."""
    app = get_object_or_404(published_apps(), pk=pk)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            messages.success(
                request,
                f'Thanks — your report about “{app.name}” was received. '
                f'Our team will review it. You can also email support if needed.',
            )
            ActivityLog.log(
                user=request.user,
                app=app,
                action=ActivityLog.ACTION_UPDATE,
                message=(
                    f'Report by {request.user.username} on {app.name}: '
                    f'{form.cleaned_data["subject"]}'
                ),
            )
            return redirect('store:detail', pk=app.pk)
    else:
        form = ReportForm()
    return render(request, 'store/report.html', {'app': app, 'form': form})


@login_required
@require_GET
def about(request):
    return render(request, 'store/about.html')


@login_required
@require_GET
def privacy(request):
    return render(request, 'store/privacy.html')


@login_required
@require_GET
def terms(request):
    return render(request, 'store/terms.html')


def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def handler403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def handler500(request):
    return render(request, 'errors/500.html', status=500)
