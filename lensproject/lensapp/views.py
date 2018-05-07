# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, ListView, DeleteView

from lensapp.forms import RegistrationForm, UploadPhotoForm, EditUserProfileForm
from lensapp.models import UserProfile, User, Photo

class Home(TemplateView):
    template_name = "index.html"


class Feed(LoginRequiredMixin, ListView):
    template_name = 'feed.html'
    model = Photo
    context_object_name = 'photos'
    login_url = '/login/'

    def get_queryset(self, *args, **kwargs):
        following_users = self.request.user.profile.following.all()
        return (Photo.objects.all().filter(user__in=following_users)
                                   .order_by('-upload_date'))


class PhotoDetail(DetailView):
    model = Photo
    context_object_name = 'photo'
    template_name = 'photo_detail.html'


class UserProfile(DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'user_profile.html'
    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])


class EditUserProfile(LoginRequiredMixin, UpdateView):
    template_name = 'edit_user_profile.html'
    form_class = EditUserProfileForm
    model = UserProfile
    login_url = '/login/'

    def get_object(self):
        return self.request.user.profile
    
    def get_success_url(self, *args, **kwargs):
        return reverse(
            'user_profile', 
            kwargs={
                'username': self.object.user.username
            }
        )


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


class UploadPhoto(LoginRequiredMixin, CreateView):
    model = Photo
    form_class = UploadPhotoForm
    login_url = '/login/'
    template_name = 'photo_upload.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UploadPhoto, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse(
            'user_profile', 
            kwargs={
                'username': self.request.user.username,
            }
        )


class DeletePhoto(DeleteView):
    model = Photo
    template_name = 'photo_delete.html'

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
