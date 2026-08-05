from django.contrib import admin

from .models import ActivityLog, App, Screenshot, SiteSettings


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 1


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'version',
        'is_published',
        'is_featured',
        'platform_label',
        'android_download_count',
        'windows_download_count',
        'created_at',
    )
    list_filter = ('is_published', 'is_featured', 'is_verified', 'created_at')
    search_fields = ('name', 'description', 'version', 'changelog')
    list_editable = ('is_published', 'is_featured')
    readonly_fields = (
        'android_download_count',
        'windows_download_count',
        'android_sha256',
        'windows_sha256',
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)
    inlines = [ScreenshotInline]
    fieldsets = (
        ('App info', {
            'fields': (
                'name', 'description', 'version', 'changelog', 'requirements', 'icon',
            ),
        }),
        ('Visibility', {
            'fields': ('is_published', 'is_featured', 'is_verified'),
        }),
        ('Android platform', {
            'fields': ('android_file', 'android_download_count', 'android_sha256'),
        }),
        ('Windows platform', {
            'fields': ('windows_file', 'windows_download_count', 'windows_sha256'),
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'app_name', 'user', 'message')
    list_filter = ('action', 'created_at')
    search_fields = ('message', 'app_name')
    readonly_fields = ('created_at',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
