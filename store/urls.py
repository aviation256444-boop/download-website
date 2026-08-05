from django.urls import path

from . import auth_views, dashboard, views

app_name = 'store'

urlpatterns = [
    # Auth
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('account/', auth_views.account_view, name='account'),
    path('dashboard/login/', auth_views.login_view, name='dashboard_login'),

    # Storefront
    path('', views.home, name='home'),
    path('app/<int:pk>/', views.app_detail, name='detail'),
    path('app/<int:pk>/report/', views.report_app, name='report'),
    path('download/<int:pk>/<str:platform>/', views.download_app, name='download'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),

    # Dashboard
    path('dashboard/logout/', dashboard.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', dashboard.dashboard_home, name='dashboard'),
    path('dashboard/export/', dashboard.dashboard_export, name='dashboard_export'),
    path('dashboard/apps/new/', dashboard.dashboard_app_create, name='dashboard_app_create'),
    path(
        'dashboard/apps/<int:pk>/edit/',
        dashboard.dashboard_app_edit,
        name='dashboard_app_edit',
    ),
    path(
        'dashboard/apps/<int:pk>/success/',
        dashboard.dashboard_app_success,
        name='dashboard_app_success',
    ),
    path(
        'dashboard/apps/<int:pk>/delete/',
        dashboard.dashboard_app_delete,
        name='dashboard_app_delete',
    ),
]
