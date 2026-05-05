from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    phone      = forms.CharField(max_length=15, required=True)
    birthday   = forms.DateField(
                     required=True,
                     widget=forms.DateInput(attrs={'type': 'date'}),
                     help_text="Required for account recovery")

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'phone', 'birthday',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['placeholder']   = 'Choose a username'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Your first name'
        self.fields['last_name'].widget.attrs['placeholder']  = 'Your last name'
        self.fields['email'].widget.attrs['placeholder']      = 'your@email.com'
        self.fields['phone'].widget.attrs['placeholder']      = '01XXXXXXXXX'
        self.fields['password1'].widget.attrs['placeholder']  = 'Create password'
        self.fields['password2'].widget.attrs['placeholder']  = 'Confirm password'
        self.fields['username'].help_text  = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
            user.profile.phone    = self.cleaned_data['phone']
            user.profile.birthday = self.cleaned_data['birthday']
            user.profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name  = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    email      = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )

    class Meta:
        model  = UserProfile
        fields = ['phone', 'address', 'bio']
        widgets = {
            'phone':   forms.TextInput(attrs={
                           'class': 'form-control',
                           'placeholder': '01XXXXXXXXX'}),
            'address': forms.Textarea(attrs={
                           'class': 'form-control',
                           'rows': 2,
                           'placeholder': 'Your address'}),
            'bio':     forms.Textarea(attrs={
                           'class': 'form-control',
                           'rows': 3,
                           'placeholder': 'Tell workers about your family...'}),
        }


class PasswordResetForm(forms.Form):
    """Custom password reset — no email, uses birthday verification."""
    email    = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Enter the birthday you registered with"
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        if p1 and len(p1) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters.")
        return cleaned