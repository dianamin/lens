from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views


from lensapp import views 

urlpatterns = [
	url(r'^$', views.Home.as_view(), name='home'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^login/$',
        auth_views.login, 
        {
            'template_name': 'login.html',
            'redirect_authenticated_user': True
        },
        name='login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'logout.html', 'next_page': '/'},
        name='logout'),
    url(r'^user/stalk/(?P<username>\w+)/$', 
    	views.UserProfile.as_view(), 
    	name='user_profile'),
    url(r'^user/edit/$',
        views.EditUserProfile.as_view(),
        name='edit_user_profile'),
    url(r'^upload_photo/$', 
    	views.UploadPhoto.as_view(), 
    	name='upload_photo'),
	url(r'^ajax/follow_user/(?P<username>\w+)/$', 
		views.FollowUserAjax.as_view(),
        name='follow_user'),
    url(r'^ajax/like_photo/(?P<photo_pk>\w+)/$', 
        views.LikePhotoAjax.as_view(),
		name='like_photo'),
    url(r'^feed/$', views.Feed.as_view(), name='feed'),
    url(r'^photo/(?P<pk>[0-9]+)/$', 
        views.PhotoDetail.as_view(),
        name='photo_detail'),
    url(r'^photo/(?P<pk>[0-9]+)/delete$', 
        views.DeletePhoto.as_view(),
        name='delete_photo'),
    url(r'^account_activation_sent',
        views.AccountActivationSent.as_view(),
        name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>\w+)/(?P<token>[\w-]+)',
        views.Activate.as_view(),
        name='activate'),
    url(r'^password_reset/$',
        auth_views.password_reset,
        {
            'template_name': 'password_reset_form.html',
            'email_template_name': 'password_reset_email.html',
            
        },
        name='password_reset'),
    url(r'^password_reset/done/$',
        auth_views.password_reset_done,
        {
            'template_name': 'password_reset_done.html',
        },
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {
            'template_name': 'password_reset_confirm.html',
        },
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_views.password_reset_complete,
        {
            'template_name': 'password_reset_complete.html',
        },
        name='password_reset_complete'),
]
