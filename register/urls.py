from django.conf.urls import url
from . import views
from .views import RegisterView, LogInView, LogOutView, AllUsersView, EditProfileView, ProfileDetailView, \
    ChangePasswordView, CityAutocompleteView, SendFriendRequestView

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LogInView.as_view(), name='login'),
    url(r'^logout/$', LogOutView.as_view(), name='logout'),
    url(r'^profile/(?P<pk>\d+)$', ProfileDetailView.as_view(), name='profile'),
    url(r'^users/$', AllUsersView.as_view(), name='all_users'),
    url(r'^edit/(?P<pk>\d+)$', EditProfileView.as_view(), name='edit_profile'),
    url(r'^password/$', ChangePasswordView.as_view()),
    url(r'^city/$', CityAutocompleteView.as_view()),
    url(r'^send_request/(?P<pk>\d+)$', SendFriendRequestView.as_view(), name='send_request'),



    url(r'^success/$', views.success, name='success'),
]
