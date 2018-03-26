# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView, DetailView, CreateView

from lensapp.forms import RegistrationForm, UploadPhotoForm
from lensapp.models import UserProfile, User, Photo

class HomeView(TemplateView):
    template_name = "index.html"


class UserProfile(DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'user_profile.html'
    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        return render(request, 'registration.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})


class UploadPhotoView(LoginRequiredMixin, CreateView):
    template_name = 'upload_photo.html'
    form_class = UploadPhotoForm
    model = Photo

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UploadPhotoView, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse(
            'user_profile', 
            kwargs={
                'username': self.request.user.username,
            }
        )

def follow_user(request, username):
    if request.method == 'GET':
        user = User.objects.get(username=username)
        if user == request.user:
            return JsonResponse({})
        if not (user in request.user.profile.following.all()):
            request.user.profile.following.add(user)
        else:
            request.user.profile.following.remove(user)
        request.user.profile.save()
        return JsonResponse({})
