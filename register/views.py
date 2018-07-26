import json
from django.http import HttpResponse
from django.views.generic.edit import FormMixin
from django.db.models import Q
from .notifications import send_register_sms, city_autocomplete,\
    get_friendship_request, get_friendship_status
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib import auth
from .forms import RegistrationForm, ChangeForm, SearchForm
from .models import User, FriendshipStatus
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View, TemplateView


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

    def get_context_data(self, **kwargs):
        sender = None
        if self.request.user.is_authenticated:
            sender = self.request.user
        receiver = User.objects.get(pk=self.object.id)
        if sender:
            status = get_friendship_request(sender, receiver)
            kwargs['status'] = get_friendship_status(status, sender)
        return super().get_context_data(**kwargs)


class AllUsersView(FormMixin, ListView):
    template_name = 'allusers.html'
    model = User
    form_class = SearchForm
    filter_field = ['city']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.get_initial()
        if params:
            return qs.filter(**params)
        return qs

    def get_initial(self):
        params = dict()
        for f in self.filter_field:
            f_value = self.request.GET.get(f)
            if f_value:
                params[f] = f_value
        return params


class EditProfileView(UpdateView):
    template_name = 'edit_profile.html'
    form_class = ChangeForm
    model = User
    success_url = '/'


class ChangePasswordView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = '/success/'


class CityAutocompleteView(View):
    def get(self, request, *args, **kwargs):
        city = request.GET.get('term', '')

        return HttpResponse(json.dumps({'err': 'nil', 'results': city_autocomplete(city)}),
                            content_type='application/json')


class SendFriendRequestView(View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            sender = self.request.user
            receiver = User.objects.get(pk=kwargs['pk'])
            friend_request = FriendshipStatus(
                sender=sender,
                receiver=receiver,
                status=False
            )
            friend_request.save()
        return redirect('/profile/' + kwargs['pk'])


class NotificationView(TemplateView):
    template_name = 'notifications.html'

    def get(self, request, *args, **kwargs):
        status = FriendshipStatus.objects.filter(status=False, receiver=self.request.user)
        request_id = []
        request_name = []
        if status:
            for value in status:
                request_id.append(value.id)
                request_name.append(value.sender)
        return self.render_to_response(context={'sender': request_name,
                                                'sender_id': request_id})


class AddToFriendView(TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            sender = self.request.user
            receiver = User.objects.get(pk=kwargs['pk'])
            friend_request = FriendshipStatus.objects.get(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
            )
            friend_request.status = True
            friend_request.save()
        return redirect('all_users')


class RemoveFromFriendView(TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            sender = self.request.user
            receiver = User.objects.get(pk=kwargs['pk'])
            friend_request = FriendshipStatus.objects.get(
                Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
            )

            friend_request.delete()
        return redirect('/profile/' + kwargs['pk'])


class FriendsView(ListView):
    template_name = 'friends.html'
    model = User

    def get_queryset(self):
        friends_request = FriendshipStatus.objects.filter(
            (Q(sender=self.request.user) | Q(receiver=self.request.user)) & Q(status=True)
        )
        return friends_request


def success(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        context = {'user': request.user}
        return render(request, 'success.html', context)
