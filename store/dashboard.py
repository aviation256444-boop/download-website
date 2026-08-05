import csv

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import AppForm, ScreenshotFormSet
from .models import ActivityLog, App


def staff_required(view_func):
    """Require an authenticated staff user (no redirect loop for normal users)."""

    @login_required(login_url='store:login')
    def _wrapped(request, *args, **kwargs):
        if not (request.user.is_active and request.user.is_staff):
            messages.error(
                request,
                'Staff access is required for the management dashboard.',
            )
            return redirect('store:home')
        return view_func(request, *args, **kwargs)

    return _wrapped


@require_http_methods(['POST', 'GET'])
def dashboard_logout(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('store:login')


@staff_required
@require_http_methods(['GET', 'POST'])
def dashboard_home(request):
    """Dashboard overview: stats, bulk actions, activity, searchable list."""
    if request.method == 'POST':
        action = request.POST.get('bulk_action', '')
        ids = request.POST.getlist('app_ids')
        qs = App.objects.filter(pk__in=ids)
        if not ids:
            messages.warning(request, 'Select at least one app.')
        elif action == 'delete':
            count = qs.count()
            for app in qs:
                ActivityLog.log(
                    user=request.user,
                    app=None,
                    action=ActivityLog.ACTION_DELETE,
                    message=f'{request.user.username} deleted “{app.name}”',
                )
                if app.android_file:
                    app.android_file.delete(save=False)
                if app.windows_file:
                    app.windows_file.delete(save=False)
                if app.icon:
                    app.icon.delete(save=False)
                for shot in app.screenshots.all():
                    shot.image.delete(save=False)
                app.delete()
            messages.success(request, f'Deleted {count} app(s).')
        elif action == 'publish':
            qs.update(is_published=True)
            messages.success(request, f'Published {qs.count()} app(s).')
        elif action == 'unpublish':
            qs.update(is_published=False)
            messages.success(request, f'Unpublished {qs.count()} app(s).')
        elif action == 'feature':
            qs.update(is_featured=True)
            messages.success(request, f'Featured {qs.count()} app(s).')
        elif action == 'unfeature':
            qs.update(is_featured=False)
            messages.success(request, f'Removed featured from {qs.count()} app(s).')
        else:
            messages.warning(request, 'Unknown bulk action.')
        return redirect('store:dashboard')

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    apps = App.objects.all()

    if query:
        apps = apps.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(version__icontains=query)
        )
    if status == 'published':
        apps = apps.filter(is_published=True)
    elif status == 'draft':
        apps = apps.filter(is_published=False)
    elif status == 'featured':
        apps = apps.filter(is_featured=True)

    totals = App.objects.aggregate(
        android_downloads=Sum('android_download_count'),
        windows_downloads=Sum('windows_download_count'),
        published=Count('id', filter=Q(is_published=True)),
        drafts=Count('id', filter=Q(is_published=False)),
    )
    android_dl = totals['android_downloads'] or 0
    windows_dl = totals['windows_downloads'] or 0

    stats = {
        'total_apps': App.objects.count(),
        'published': totals['published'] or 0,
        'drafts': totals['drafts'] or 0,
        'android_apps': App.objects.exclude(android_file='').exclude(
            android_file__isnull=True
        ).count(),
        'windows_apps': App.objects.exclude(windows_file='').exclude(
            windows_file__isnull=True
        ).count(),
        'total_downloads': android_dl + windows_dl,
        'android_downloads': android_dl,
        'windows_downloads': windows_dl,
    }

    activity = ActivityLog.objects.select_related('user', 'app')[:12]

    return render(request, 'dashboard/home.html', {
        'apps': apps,
        'query': query,
        'status': status,
        'stats': stats,
        'app_count': apps.count(),
        'activity': activity,
    })


@staff_required
@require_http_methods(['GET'])
def dashboard_export(request):
    """Export apps as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="apps-export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id', 'name', 'version', 'published', 'featured',
        'android_downloads', 'windows_downloads', 'created_at',
    ])
    for app in App.objects.all():
        writer.writerow([
            app.pk,
            app.name,
            app.version,
            app.is_published,
            app.is_featured,
            app.android_download_count,
            app.windows_download_count,
            app.created_at.isoformat(),
        ])
    return response


@staff_required
@require_http_methods(['GET', 'POST'])
def dashboard_app_create(request):
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES)
        # Temporary instance so the screenshot formset can bind on create
        temp_app = form.save(commit=False) if form.is_valid() else App()
        formset = ScreenshotFormSet(request.POST, request.FILES, instance=temp_app)
        if form.is_valid() and formset.is_valid():
            app = form.save()
            formset.instance = app
            formset.save()
            ActivityLog.log(
                user=request.user,
                app=app,
                action=ActivityLog.ACTION_UPLOAD,
                message=f'{request.user.username} uploaded “{app.name}” v{app.version}',
            )
            messages.success(
                request,
                f'“{app.name}” is live.' if app.is_published else f'“{app.name}” saved as draft.',
            )
            return redirect('store:dashboard_app_success', pk=app.pk)
    else:
        form = AppForm()
        formset = ScreenshotFormSet(instance=App())

    return render(request, 'dashboard/app_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Upload new app',
        'submit_label': 'Upload app',
        'is_edit': False,
    })


@staff_required
@require_http_methods(['GET', 'POST'])
def dashboard_app_edit(request, pk):
    app = get_object_or_404(App, pk=pk)

    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES, instance=app)
        formset = ScreenshotFormSet(request.POST, request.FILES, instance=app)
        if form.is_valid() and formset.is_valid():
            was_published = app.is_published
            app = form.save()
            formset.save()
            ActivityLog.log(
                user=request.user,
                app=app,
                action=ActivityLog.ACTION_UPDATE,
                message=f'{request.user.username} updated “{app.name}”',
            )
            if was_published != app.is_published:
                ActivityLog.log(
                    user=request.user,
                    app=app,
                    action=(
                        ActivityLog.ACTION_PUBLISH
                        if app.is_published
                        else ActivityLog.ACTION_UNPUBLISH
                    ),
                    message=(
                        f'{request.user.username} '
                        f'{"published" if app.is_published else "unpublished"} “{app.name}”'
                    ),
                )
            messages.success(request, f'“{app.name}” was updated.')
            return redirect('store:dashboard_app_success', pk=app.pk)
    else:
        form = AppForm(instance=app)
        formset = ScreenshotFormSet(instance=app)

    return render(request, 'dashboard/app_form.html', {
        'form': form,
        'formset': formset,
        'app': app,
        'title': f'Edit {app.name}',
        'submit_label': 'Save changes',
        'is_edit': True,
    })


@staff_required
@require_http_methods(['GET'])
def dashboard_app_success(request, pk):
    app = get_object_or_404(App, pk=pk)
    return render(request, 'dashboard/app_success.html', {'app': app})


@staff_required
@require_http_methods(['GET', 'POST'])
def dashboard_app_delete(request, pk):
    app = get_object_or_404(App, pk=pk)

    if request.method == 'POST':
        name = app.name
        ActivityLog.log(
            user=request.user,
            app=None,
            action=ActivityLog.ACTION_DELETE,
            message=f'{request.user.username} deleted “{name}”',
        )
        if app.android_file:
            app.android_file.delete(save=False)
        if app.windows_file:
            app.windows_file.delete(save=False)
        if app.icon:
            app.icon.delete(save=False)
        for shot in app.screenshots.all():
            shot.image.delete(save=False)
        app.delete()
        messages.success(request, f'“{name}” was deleted.')
        return redirect('store:dashboard')

    return render(request, 'dashboard/app_delete.html', {'app': app})
