from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import View

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from phonenumbers import NumberParseException

from .forms import RegistrationForm
from django.contrib.auth.models import User
import phonenumbers
from django.views.generic import CreateView, FormView


class RegisterView(CreateView):
    form_class = RegistrationForm
    model = User
    template_name = 'register.html'
    success_url = '/success/'

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(self.request, user)
            return valid
        else:
            return self.form_invalid(form)


class LogInView(LoginView):
    template_name = 'log_in.html'


class LogOutView(LogoutView):
    redirect_field_name = None


class SeeProfileView(View):
    def load_profile(self):
        user_instance = get_object_or_404(User, id=id)
        username = None
        can_edit = None
        if self.request.user.is_staff or \
                self.request.user.is_superuser or \
                self.request.user.is_authenticated:
            username = auth.get_user(self.request).username

        if user_instance.id == self.request.user.id:
            can_edit = True

        context = {
            'user': user_instance,
            'can_edit': can_edit,
            'username': username,
        }

        return render(self.request, 'profile.html', context)


def load_profile(request, id):
    user_instance = get_object_or_404(register_user, pk=id)

    print(user_instance)
    username = None
    can_edit = None
    if request.user.is_staff or \
            request.user.is_superuser or \
            request.user.is_authenticated:
        username = auth.get_user(request)

    if user_instance.id == request.user.id:
        can_edit = True

    context = {
        'user': user_instance,
        'can_edit': can_edit,
        'username': username,
    }

    return render(request, 'profile.html', context)




def success(request):
    print(auth.get_user(request))
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        context = {'user': request.user}
        return render(request, 'success.html', context)
