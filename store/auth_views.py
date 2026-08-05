from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegisterForm


def _google_configured():
    """True when Google OAuth client credentials are available."""
    if getattr(settings, 'GOOGLE_CLIENT_ID', '') and getattr(settings, 'GOOGLE_CLIENT_SECRET', ''):
        return True
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        return SocialApp.objects.filter(provider='google', sites=site).exists()
    except Exception:
        return False


def _post_login_redirect(request, user):
    """Honor ?next=; staff go to dashboard by default, others to the store."""
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    if user.is_staff:
        return redirect('store:dashboard')
    return redirect('store:home')


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    Mandatory sign-in page with both methods:
      1) Manual form (username + password)
      2) Google OAuth
    """
    if request.user.is_authenticated:
        return _post_login_redirect(request, request.user)

    form = LoginForm(request, data=request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_username()}!')
            return _post_login_redirect(request, user)
        error = 'Invalid username or password. Please try again.'

    next_url = request.GET.get('next', '')
    return render(request, 'auth/login.html', {
        'form': form,
        'error': error,
        'next': next_url,
        'resume_path': next_url,
        'google_enabled': _google_configured(),
    })


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """Manual registration — user fills in name, email, username, password."""
    if request.user.is_authenticated:
        return redirect('store:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Account created. You are now signed in.')
        return redirect('store:home')

    return render(request, 'auth/register.html', {
        'form': form,
        'google_enabled': _google_configured(),
    })


@require_http_methods(['POST', 'GET'])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('store:login')


@login_required
@require_http_methods(['GET'])
def account_view(request):
    """Simple account overview for the signed-in user."""
    return render(request, 'auth/account.html', {'user_obj': request.user})
