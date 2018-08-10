import json
import csv

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, StreamingHttpResponse
from django.views.generic.edit import FormMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import render, redirect
from django.contrib import auth
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View, TemplateView
from django.core.cache import cache

from .forms import RegistrationForm, ChangeForm, SearchForm
from .models import User, FriendshipStatus
from .notifications import send_register_sms, city_autocomplete, get_friendship_request, get_friendship_status, \
    search_near_users, CsrfExemptMixin, AuthMixin, ProtectedViewMixin


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
            kwargs['friends'] = self.request.user.friends.filter(user=sender)
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
            create_friend_request = FriendshipStatus(
                sender=sender,
                receiver=receiver,
                status=False
            )
            create_friend_request.save()
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
            friend_request = get_friendship_request(sender, receiver)
            friend_request.receiver.friends.add(receiver)
            friend_request.sender.friends.add(sender)
            friend_request.delete()

        return redirect('all_users')


class RemoveFromFriendView(TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            sender = self.request.user
            receiver = User.objects.get(pk=kwargs['pk'])
            self.request.user.friends.remove(receiver)
            receiver.friends.remove(sender)
        return redirect('/profile/' + kwargs['pk'])


class FriendsView(ListView):
    template_name = 'friends.html'
    model = User

    def get_queryset(self):
        return self.request.user.friends.all()


class NearestUserView(TemplateView):
    template_name = 'nearest.html'

    def get(self, request, *args, **kwargs):
        current_user_city = self.request.user.city
        if not current_user_city:
            return self.render_to_response(context={'city': current_user_city})
        users = User.objects.exclude(pk=self.request.user.id).exclude(city='')
        distances = list()
        for user in users:
            cache_key = '_'.join(sorted([str(self.request.user.id), str(user.id)]))
            distance = cache.get(cache_key)
            if not distance:
                distance = search_near_users(current_user_city, user.city)
                if not distance:
                    continue
            cache.set(cache_key, distance)
            distances.append((user, round((distance/1000), 1)))
        nearest = [(u, d) for u, d in sorted(distances, key=lambda x:x[1])]
        return self.render_to_response(context={'city': current_user_city,
                                                'nearest': nearest[:5]}
                                       )


class GetAccessTokenView(CsrfExemptMixin, AuthMixin, View):

    def post(self, request, *args, **kwargs):
        grant = request.POST.get('grant_type')
        if grant != 'client_credentials':
            return HttpResponseForbidden()
        token = self.app.create_token()
        return JsonResponse(status=200, data=token.make_response_body())


class ProtectedDataView(CsrfExemptMixin, ProtectedViewMixin, View):
    def get(self, request, *args, ** kwargs):
        users = User.objects.all()
        json_res = []
        for user in users:
            json_obj = dict(
                username=user.username,
                mail=user.email,
                telephone=user.phone_number,
            )
            json_res.append(json_obj)
        return JsonResponse({'results': json_res})


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class ReturnCsvDataView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        filename = "{}.csv".format('users')
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        headers = ('id', 'username', 'email', 'telephone', 'first name', 'last name', 'city from')
        rows = [headers]
        print(rows)
        rows.extend(users.values_list('pk', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'city'))
        print(rows)
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


# class


def success(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        context = {'user': request.user}
        return render(request, 'success.html', context)
