from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class RegistrationForm(UserCreationForm):
    email = forms.CharField(max_length=75, required=True)

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

    # def clean_number(self):
    #     self.cleaned_data['phone_number'] = '+%s' % self.cleaned_data['phone_number'].replace('+', '')
    #     valid = True
    #     try:
    #         phone = phonenumbers.parse(self.cleaned_data['phone_number'], None)
    #     except NumberParseException:
    #         valid = False
    #     else:
    #         if not phonenumbers.is_valid_number(phone):
    #             valid = False
    #     if valid is False:
    #         raise ValidationError('Phone number is not valid', code='invalid')
    #     return self.cleaned_data['phone_number']


# class LoginForm(forms.ModelForm):
#
#     class Meta:
#         model = User
#         fields = [
#             'username',
#             'email',
#             'phone_number',
#             'password',
#         ]
