"""
URL configuration for config project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # django-allauth (Google OAuth callbacks live under /accounts/)
    path('accounts/', include('allauth.urls')),
    path('', include('store.urls')),
]

handler404 = 'store.views.handler404'
handler403 = 'store.views.handler403'
handler500 = 'store.views.handler500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
