from django.conf.urls import url
# from django.urls import include
from oauth2_provider.views import AuthorizationView, TokenView, RevokeTokenView

from . import views
from .views import RegisterView, LogInView, LogOutView, AllUsersView, EditProfileView, ProfileDetailView, \
    ChangePasswordView, CityAutocompleteView, SendFriendRequestView, NotificationView, AddToFriendView, \
    RemoveFromFriendView, FriendsView, NearestUserView, GetAccessTokenView, ProtectedDataView, ReturnCsvDataView

urlpatterns = [

    url(r'^authorize/?$', AuthorizationView.as_view(), name="authorize"),
    url(r'^token/?$', TokenView.as_view(), name="token"),
    url(r'^revoke_token/?$', RevokeTokenView.as_view(), name="revoke-token"),

    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LogInView.as_view(), name='login'),
    url(r'^logout/$', LogOutView.as_view(), name='logout'),
    url(r'^profile/(?P<pk>\d+)$', ProfileDetailView.as_view(), name='profile'),
    url(r'^users/$', AllUsersView.as_view(), name='all_users'),
    url(r'^edit/(?P<pk>\d+)$', EditProfileView.as_view(), name='edit_profile'),
    url(r'^password/$', ChangePasswordView.as_view()),
    url(r'^city/$', CityAutocompleteView.as_view()),
    url(r'^send_request/(?P<pk>\d+)$', SendFriendRequestView.as_view(), name='send_request'),
    url(r'^add_to_friend/(?P<pk>\d+)$', AddToFriendView.as_view(), name='add_to_friend'),
    url(r'^remove/(?P<pk>\d+)$', RemoveFromFriendView.as_view(), name='remove'),
    url(r'^notification/$', NotificationView.as_view(), name='notification'),
    url(r'^friends/$', FriendsView.as_view(), name='friends'),
    url(r'^nearest_users/$', NearestUserView.as_view(), name='nearest_users'),
    url(r'^token/?$', GetAccessTokenView.as_view()),
    url(r'^protected_data/?$', ProtectedDataView.as_view()),
    url(r'^get_csv_data/?$', ReturnCsvDataView.as_view(), name='get_csv'),


    url(r'^success/$', views.success, name='success'),
]
