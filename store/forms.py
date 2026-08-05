from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import inlineformset_factory

from .models import App, Screenshot

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Manual username + password sign-in."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autocomplete': 'username',
            'autofocus': True,
        }),
        label='Username',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'id': 'id_password',
        }),
        label='Password',
    )


class RegisterForm(UserCreationForm):
    """Manual registration — fill in username, email, and password."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        }),
        label='Email',
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'First name',
            'autocomplete': 'given-name',
        }),
        label='First name',
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        }),
        label='Last name',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
            'id': 'id_password1',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
            'id': 'id_password2',
        })

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class AppForm(forms.ModelForm):
    """Create/edit form with platform-specific file uploads."""

    clear_android = forms.BooleanField(
        required=False,
        label='Remove current Android APK',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    clear_windows = forms.BooleanField(
        required=False,
        label='Remove current Windows EXE',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    clear_icon = forms.BooleanField(
        required=False,
        label='Remove current icon',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = App
        fields = (
            'name',
            'description',
            'version',
            'changelog',
            'requirements',
            'icon',
            'android_file',
            'windows_file',
            'is_published',
            'is_featured',
            'is_verified',
        )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. CrossNote',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the app, features, audience…',
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 1.0.0',
            }),
            'changelog': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What’s new in this version…',
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Android 8.0+ · Windows 10/11 64-bit',
            }),
            'icon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-dropzone': 'icon',
            }),
            'android_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.apk,application/vnd.android.package-archive',
                'data-dropzone': 'android',
            }),
            'windows_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.exe,application/x-msdownload,application/octet-stream',
                'data-dropzone': 'windows',
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'App name',
            'description': 'Description',
            'version': 'Version',
            'changelog': "What's new",
            'requirements': 'System requirements',
            'icon': 'App icon (optional)',
            'android_file': 'Android APK',
            'windows_file': 'Windows EXE',
            'is_published': 'Published (visible in store)',
            'is_featured': 'Featured on homepage',
            'is_verified': 'Verified by admin badge',
        }
        help_texts = {
            'android_file': 'Upload a .apk file for Android users (max 200 MB).',
            'windows_file': 'Upload a .exe file for Windows users (max 200 MB).',
            'icon': 'PNG, JPG, GIF, WEBP, or SVG.',
            'is_published': 'Uncheck to save as draft (hidden from users).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop('clear_android')
            self.fields.pop('clear_windows')
            self.fields.pop('clear_icon')

    def clean(self):
        cleaned = super().clean()
        instance = self.instance

        android = cleaned.get('android_file')
        windows = cleaned.get('windows_file')
        clear_android = cleaned.get('clear_android', False)
        clear_windows = cleaned.get('clear_windows', False)

        if instance.pk:
            if android:
                will_have_android = True
            elif clear_android:
                will_have_android = False
            else:
                will_have_android = bool(instance.android_file)

            if windows:
                will_have_windows = True
            elif clear_windows:
                will_have_windows = False
            else:
                will_have_windows = bool(instance.windows_file)
        else:
            will_have_android = bool(android)
            will_have_windows = bool(windows)

        if not will_have_android and not will_have_windows:
            raise forms.ValidationError(
                'Upload at least one platform file: Android APK and/or Windows EXE.'
            )

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.instance.pk:
            if self.cleaned_data.get('clear_android') and not self.cleaned_data.get('android_file'):
                if instance.android_file:
                    instance.android_file.delete(save=False)
                instance.android_file = None
                instance.android_sha256 = ''
            if self.cleaned_data.get('clear_windows') and not self.cleaned_data.get('windows_file'):
                if instance.windows_file:
                    instance.windows_file.delete(save=False)
                instance.windows_file = None
                instance.windows_sha256 = ''
            if self.cleaned_data.get('clear_icon') and not self.cleaned_data.get('icon'):
                if instance.icon:
                    instance.icon.delete(save=False)
                instance.icon = None

        if commit:
            instance.save()
            # Force hash refresh when a new platform file was uploaded
            force = bool(
                self.cleaned_data.get('android_file')
                or self.cleaned_data.get('windows_file')
            )
            instance.refresh_checksums(force=force)
            self.save_m2m()
        return instance


class ScreenshotForm(forms.ModelForm):
    class Meta:
        model = Screenshot
        fields = ('image', 'caption', 'sort_order')
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Optional caption',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': 0,
            }),
        }


ScreenshotFormSet = inlineformset_factory(
    App,
    Screenshot,
    form=ScreenshotForm,
    extra=2,
    can_delete=True,
    max_num=8,
)


class ReportForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Brief summary of the issue',
        }),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe the problem…',
        }),
    )
