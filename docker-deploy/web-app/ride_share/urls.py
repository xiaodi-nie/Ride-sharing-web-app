from django.urls import re_path,path
from . import views

app_name = 'ride_share'
urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^logout/', views.logout, name='logout'),
    re_path(r'^user/(?P<pk>\d+)/profile/$', views.profile, name='profile'),
    re_path(r'^user/(?P<pk>\d+)/profile/update/$', views.profile_update, name='profile_update'),
    re_path(r'^user/(?P<pk>\d+)/pwdchange/$', views.pwd_change, name='pwd_change'),
    re_path(r'^user/(?P<pk>\d+)/register_driver/$', views.register_driver, name='register_driver'),
    re_path(r'^user/(?P<pk>\d+)/request_car/$', views.request_car, name='request_car'),
    re_path(r'^user/(?P<pk>\d+)/current_trip/$', views.current_trip, name='current_trip'),
    re_path(r'^user/(?P<pk>\d+)/current_trip_update/$', views.current_trip_update, name='current_trip_update'),
    re_path(r'^user/(?P<pk>\d+)/driver_search_order/$', views.driver_search_order, name='driver_search_order'),
    re_path(r'^user/(?P<pk>\d+)/share_car/$', views.share_car, name='share_car'),
    re_path(r'^user/(?P<pk>\d+)/(?P<trip_id>\d+)/join_ride/$', views.join_ride, name='join_ride'),
    re_path(r'^user/(?P<pk>\d+)/past_trip/$', views.past_trip, name='past_trip'),


]