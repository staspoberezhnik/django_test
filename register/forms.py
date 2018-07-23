from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=75, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password1',
            'password2',
            'photo',
        ]


class ChangeForm(UserChangeForm):
    email = forms.EmailField(max_length=75, required=True)

    class Meta:
        model = User
        fields = {
            'password',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'photo',
        }
