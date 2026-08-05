import hashlib
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validate_apk_file(value):
    """Only allow .apk uploads for Android."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.apk':
        raise ValidationError('Android file must be a .apk file.')


def validate_exe_file(value):
    """Only allow .exe uploads for Windows."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.exe':
        raise ValidationError('Windows file must be a .exe file.')


def validate_icon_image(value):
    """Only allow common image formats for app icons."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'):
        raise ValidationError(
            'Unsupported image type. Use PNG, JPG, GIF, WEBP, or SVG.'
        )


def _file_size_display(file_field):
    """Human-readable size for a FileField."""
    if not file_field:
        return '—'
    try:
        size = file_field.size
    except (OSError, ValueError):
        return '—'
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size < 1024:
            return f'{size:.1f} {unit}' if unit != 'B' else f'{size} {unit}'
        size /= 1024
    return f'{size:.1f} TB'


def _sha256_of_field(file_field):
    """Compute SHA-256 hex digest of a stored file."""
    if not file_field:
        return ''
    try:
        file_field.open('rb')
        h = hashlib.sha256()
        for chunk in file_field.chunks():
            h.update(chunk)
        file_field.close()
        return h.hexdigest()
    except (OSError, ValueError):
        return ''


class App(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    version = models.CharField(max_length=50)
    changelog = models.TextField(
        blank=True,
        help_text='What\'s new in this version.',
        verbose_name="What's new",
    )
    requirements = models.TextField(
        blank=True,
        help_text='e.g. Android 8+ / Windows 10+',
        verbose_name='System requirements',
    )

    android_file = models.FileField(
        upload_to='apps/android/',
        blank=True,
        null=True,
        validators=[validate_apk_file],
        help_text='Upload the Android APK (.apk only).',
        verbose_name='Android APK',
    )
    windows_file = models.FileField(
        upload_to='apps/windows/',
        blank=True,
        null=True,
        validators=[validate_exe_file],
        help_text='Upload the Windows installer (.exe only).',
        verbose_name='Windows EXE',
    )

    icon = models.ImageField(
        upload_to='icons/',
        blank=True,
        null=True,
        validators=[validate_icon_image],
    )

    is_published = models.BooleanField(
        default=True,
        help_text='Unpublished (draft) apps are hidden from the storefront.',
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Featured apps appear at the top of the homepage.',
    )
    is_verified = models.BooleanField(
        default=True,
        help_text='Show a “Verified by admin” trust badge.',
    )

    android_download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Android downloads',
    )
    windows_download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Windows downloads',
    )
    android_sha256 = models.CharField(max_length=64, blank=True)
    windows_sha256 = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'App'
        verbose_name_plural = 'Apps'

    def __str__(self):
        return f'{self.name} (v{self.version})'

    def clean(self):
        super().clean()
        if not self.android_file and not self.windows_file:
            raise ValidationError(
                'Upload at least one platform file: Android APK and/or Windows EXE.'
            )

    def refresh_checksums(self, force=False):
        """Recompute SHA-256 for platform files (call after file changes)."""
        updated_fields = []
        if self.android_file and (force or not self.android_sha256):
            digest = _sha256_of_field(self.android_file)
            if digest and digest != self.android_sha256:
                self.android_sha256 = digest
                updated_fields.append('android_sha256')
        if self.windows_file and (force or not self.windows_sha256):
            digest = _sha256_of_field(self.windows_file)
            if digest and digest != self.windows_sha256:
                self.windows_sha256 = digest
                updated_fields.append('windows_sha256')
        if updated_fields and self.pk:
            type(self).objects.filter(pk=self.pk).update(
                **{f: getattr(self, f) for f in updated_fields}
            )

    @property
    def download_count(self):
        return self.android_download_count + self.windows_download_count

    @property
    def has_android(self):
        return bool(self.android_file)

    @property
    def has_windows(self):
        return bool(self.windows_file)

    @property
    def platform_labels(self):
        labels = []
        if self.has_android:
            labels.append('Android')
        if self.has_windows:
            labels.append('Windows')
        return labels

    @property
    def platform_label(self):
        labels = self.platform_labels
        return ', '.join(labels) if labels else 'No file'

    @property
    def android_file_size_display(self):
        return _file_size_display(self.android_file)

    @property
    def windows_file_size_display(self):
        return _file_size_display(self.windows_file)

    @property
    def status_label(self):
        return 'Published' if self.is_published else 'Draft'

    def get_file_for_platform(self, platform):
        platform = (platform or '').lower()
        if platform == 'android' and self.android_file:
            return self.android_file
        if platform == 'windows' and self.windows_file:
            return self.windows_file
        return None

    def get_sha256_for_platform(self, platform):
        platform = (platform or '').lower()
        if platform == 'android':
            return self.android_sha256
        if platform == 'windows':
            return self.windows_sha256
        return ''


class Screenshot(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='screenshots/', validators=[validate_icon_image])
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'Screenshot for {self.app.name}'


class ActivityLog(models.Model):
    ACTION_UPLOAD = 'upload'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_PUBLISH = 'publish'
    ACTION_UNPUBLISH = 'unpublish'
    ACTION_DOWNLOAD = 'download'
    ACTION_CHOICES = [
        (ACTION_UPLOAD, 'Uploaded'),
        (ACTION_UPDATE, 'Updated'),
        (ACTION_DELETE, 'Deleted'),
        (ACTION_PUBLISH, 'Published'),
        (ACTION_UNPUBLISH, 'Unpublished'),
        (ACTION_DOWNLOAD, 'Downloaded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    app_name = models.CharField(max_length=200, blank=True)
    app = models.ForeignKey(
        App,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message

    @classmethod
    def log(cls, *, user=None, app=None, action='', message=''):
        return cls.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            app=app,
            app_name=app.name if app else '',
            action=action,
            message=message,
        )


class SiteSettings(models.Model):
    """Singleton-style site branding / contact."""
    support_email = models.EmailField(default='support@appstore.local')
    site_tagline = models.CharField(
        max_length=200,
        default='Discover & download Android and Windows apps',
    )
    about_text = models.TextField(
        blank=True,
        default=(
            'AppStore is a simple private app distribution portal. '
            'Admins upload Android APK and Windows EXE builds; signed-in users browse and download them.'
        ),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return 'Site settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
