from .notifications import send_register_sms
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib import auth
from .forms import RegistrationForm, ChangeForm
from .models import User
from django.views.generic import CreateView, UpdateView, DetailView, ListView


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
        receiver = form.cleaned_data.get('phone_number')
        if user is not None:
            send_register_sms(username, receiver)
            auth.login(self.request, user)
            return valid
        else:
            return self.form_invalid(form)


class LogInView(LoginView):
    template_name = 'log_in.html'


class LogOutView(LogoutView):
    redirect_field_name = None


class ProfileDetailView(DetailView):
    template_name = 'profile.html'
    model = User


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
    success_url = '/'


class ChangePasswordView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = '/success/'


def success(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        context = {'user': request.user}
        return render(request, 'success.html', context)
