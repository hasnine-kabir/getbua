from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    phone      = forms.CharField(max_length=15, required=True)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to every field automatically
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['autocomplete'] = 'off'

        # Custom placeholders
        self.fields['username'].widget.attrs['placeholder']   = 'Choose a username'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Your first name'
        self.fields['last_name'].widget.attrs['placeholder']  = 'Your last name'
        self.fields['email'].widget.attrs['placeholder']      = 'your@email.com'
        self.fields['phone'].widget.attrs['placeholder']      = '01XXXXXXXXX'
        self.fields['password1'].widget.attrs['placeholder']  = 'Create password'
        self.fields['password2'].widget.attrs['placeholder']  = 'Confirm password'

        # Remove default help texts (optional clean look)
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
            # Save phone in UserProfile (Step 2.2)
            user.profile.phone = self.cleaned_data['phone']
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