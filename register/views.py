from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import View, TemplateView, ListView

from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from .forms import RegistrationForm, ChangeForm
from .models import User
import phonenumbers
from django.views.generic import CreateView, FormView, UpdateView


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


class SeeProfileView(ListView):
    template_name = 'profile.html'

    def get_queryset(self):
        return get_object_or_404(User, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        user_instance = get_object_or_404(User, id=self.kwargs['id'])
        username = None
        can_edit = None
        print(user_instance.id, self.request.user.id)
        if self.request.user.is_staff or \
                self.request.user.is_superuser or \
                self.request.user.is_authenticated:
            username = auth.get_user(self.request).username
        print('hello')
        if user_instance.id == self.request.user.id:
            can_edit = True
        context = {
            'user': user_instance,
            'can_edit': can_edit,
            'username': username,
        }
        return context


class AllUsersView(ListView):
    template_name = 'allusers.html'
    model = User

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        user_instance = User.objects.all()
        context = {
            'users': user_instance,
        }
        return context


class EditProfileView(UpdateView):
    template_name = 'edit_profile.html'
    form_class = ChangeForm
    model = User

    # def get(self, request, *args, **kwargs):
    #     self.object = get_object_or_404(User, id=self.kwargs['id'])
    #     return super(self.object).get(request, *args, **kwargs)


def success(request):
    print(auth.get_user(request))
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        context = {'user': request.user}
        return render(request, 'success.html', context)
