from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from lensapp import views

urlpatterns = [
	url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout,
        {'template_name': 'logout.html', 'next_page': '/'},
        name='logout'),
    url(r'^user/stalk/(?P<username>\w+)/$', 
    	views.UserProfile.as_view(), 
    	name='user_profile'),
    url(r'^user/edit/$',
        views.EditUserProfile.as_view(),
        name='edit_user_profile'),
    url(r'^upload_photo/$', 
    	views.UploadPhotoView.as_view(), 
    	name='upload_photo'),
	url(r'^ajax/follow_user/(?P<username>\w+)/$', 
		views.follow_user,
		name='follow_user'),
    url(r'^feed/$', views.Feed.as_view(), name='feed'),
    url(r'^photo/(?P<pk>[0-9]+)/$', 
        views.PhotoDetail.as_view(),
        name='photo_detail'),
]
