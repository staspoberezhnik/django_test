from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from decouple import config
from django.contrib import messages
from django.shortcuts import redirect


class RegisterAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        u = sociallogin.user.email
        if u.split('@')[1] != "capitalhero.com":
            messages.error(request, 'You not allowed to log in with domain name -' + u.split('@')[1])
            raise ImmediateHttpResponse(redirect('http://127.0.0.1:8000/login/'))
