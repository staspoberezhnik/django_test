from django.forms import HiddenInput

from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django_select2.forms import HeavySelect2Widget, Select2Widget


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=75, required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password1',
            'password2',
            'city',
            'photo',
        )

        widgets = {
            'city': HeavySelect2Widget(
                data_url=' /city/'
            )
        }


class ChangeForm(UserChangeForm):
    email = forms.EmailField(max_length=75, required=True)
    password = forms.HiddenInput

    class Meta:
        model = User

        fields = (

            'username',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'city',
            'photo',
            'password'
        )
        widgets = {
          'city':  HeavySelect2Widget(
                data_url=' /city/'),

        }

    def __init__(self, *args, **kwargs):
        super(ChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = HiddenInput()

