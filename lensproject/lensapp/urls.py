from django.conf.urls import url
from django.contrib import admin
from lensapp import views

urlpatterns = [
	url(r'^$', views.HomeView.as_view()),
]
