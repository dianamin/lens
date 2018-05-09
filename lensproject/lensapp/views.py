# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, ListView, DeleteView

from lensapp.forms import RegistrationForm, UploadPhotoForm, EditUserProfileForm
from lensapp.models import UserProfile, User, Photo
from lensapp.helpers import activation_token

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

class Home(TemplateView):
    template_name = 'index.html'


class AccountActivationSent(TemplateView):
    template_name = 'account_activation_sent.html'


class Activate(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        uidb64 = self.kwargs['uidb64']
        token = self.kwargs['token']
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and activation_token.check_token(user, token):
            user.profile.activated = True
            user.profile.save()
            return redirect('login')
        else:
            return render(request, 'account_activation_invalid.html')


class Feed(LoginRequiredMixin, ListView):
    template_name = 'feed.html'
    model = Photo
    context_object_name = 'photos'
    login_url = '/login/'

    def get_queryset(self, *args, **kwargs):
        following_users = self.request.user.profile.following.all()
        return (Photo.objects.all().filter(user__in=following_users)
                                   .order_by('-upload_date'))


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


class Register(TemplateView):
    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        form = RegistrationForm(self.request.POST)
        if form.is_valid():
            user = form.save()

            site = get_current_site(self.request)
            subject = 'Lens Registration'
            message = render_to_string('account_activation_email.html', {
                'domain': site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'user': user,
                'token': str(activation_token.make_token(user)),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
        return render(self.request, 'registration.html', {'form': form})

    def get(self, request, *args, **kwargs):   
        if self.request.user.is_authenticated:
            return redirect('/')
        form = RegistrationForm()
        return render(self.request, 'registration.html', {'form': form})


class PhotoDetail(DetailView):
    model = Photo
    context_object_name = 'photo'
    template_name = 'photo_detail.html'


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


class FollowUserAjax(TemplateView):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])
        if user == self.request.user:
            return JsonResponse({})
        if not (user in self.request.user.profile.following.all()):
            self.request.user.profile.following.add(user)
        else:
            self.request.user.profile.following.remove(user)
        self.request.user.profile.save()
        return JsonResponse({})


class LikePhotoAjax(TemplateView):
    def get(self, request, *args, **kwargs):
        photo = Photo.objects.get(pk=kwargs['photo_pk'])
        if photo.user == self.request.user:
            return JsonResponse({})
        if not (self.request.user in photo.likes.all()):
            photo.likes.add(self.request.user)
        else:
            photo.likes.remove(self.request.user)
        photo.save()
        return JsonResponse({})
