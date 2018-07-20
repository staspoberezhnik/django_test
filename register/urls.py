from django.conf.urls import url
from . import views
from .views import RegisterView, LogInView, LogOutView, SeeProfileView

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^login/$', LogInView.as_view(), name='login'),
    url(r'^logout/$', LogOutView.as_view(), name='logout'),
    # url(r'^profile/$', SeeProfileView.as_view(), name='profile'),
    url(r'^profile/(?P<id>\d+)/$', views.load_profile, name='profile'),

    # url(r'^$', views.log_in, name='login'),
    # url(r'^register/$', views.register, name='register'),
    # url(r'^logout/$', views.log_out, name='logout'),
    url(r'^success/$', views.success, name='success'),
]


