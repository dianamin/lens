# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import (TemplateView, DetailView, CreateView,
                                    UpdateView, ListView, DeleteView)

from lensapp.forms import RegistrationForm, UploadPhotoForm, EditUserProfileForm
from lensapp.models import UserProfile, User, Photo
from lensapp.helpers import activation_token

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from random import shuffle

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
        max_photos_count = 99
        following_users = self.request.user.profile.following.all()
        return (Photo.objects.all().filter(user__in=following_users)
                                   .order_by('-upload_date'))[:max_photos_count]

    def get_context_data(self,**kwargs):
        context = super(Feed, self).get_context_data(**kwargs)
        context['title'] = 'Feed'
        return context


class Discover(ListView):
    template_name = 'feed.html'
    model = Photo
    context_object_name = 'photos'
    login_url = '/login/'

    def get_queryset(self, *args, **kwargs):
        def merge_query_sets(s1, s2):
            if s1 == None and s2 == None:
                raise Exception("Both query sets are None")
            if s1 == None:
                return s2
            if s2 == None:
                return s1
            return s1 | s2

        user_photos = []
        max_photos_count = 48
        if self.request.user.is_authenticated:
            user_photos = self.request.user.uploaded_photos.all()[:5]

        # get similar photos
        similar_photos = None
        for photo in user_photos:
            similar_photos = merge_query_sets(similar_photos,
                    photo.get_similar())

        # get new photos
        new_photos = (Photo.objects.all().order_by('-upload_date').all() \
                [:max_photos_count])

        # hacked
        similar_photos = [p for p in similar_photos] + [p for p in new_photos]

        # filter photos
        similar_photos = [p for p in similar_photos \
                if p.user != self.request.user][:max_photos_count]

        shuffle(similar_photos)

        return similar_photos

    def get_context_data(self,**kwargs):
        context = super(Discover, self).get_context_data(**kwargs)
        context['title'] = 'Discover'
        return context


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


class FollowUserAjax(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if 'username' not in kwargs:
            return JsonResponse({'error': 'No user given.'})
        if not User.objects.filter(username=kwargs['username']).exists():
            return JsonResponse({'error': 'User does not exist.'})
        user = User.objects.get(username=kwargs['username'])
        if user == self.request.user:
            return JsonResponse({})
        if not (user in self.request.user.profile.following.all()):
            self.request.user.profile.following.add(user)
        else:
            self.request.user.profile.following.remove(user)
        self.request.user.profile.save()
        return JsonResponse({})


class LikePhotoAjax(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if 'photo_pk' not in kwargs:
            return JsonResponse({'error': 'No photo given.'})
        if not Photo.objects.filter(pk=kwargs['photo_pk']).exists():
            return JsonResponse({'error': 'Photo does not exist.'})
        photo = Photo.objects.get(pk=kwargs['photo_pk'])
        if photo.user == self.request.user:
            return JsonResponse({'error': 'Don\'t like your own photo.'})
        response = {}
        if not (self.request.user in photo.likes.all()):
            photo.likes.add(self.request.user)
            response['liked'] = True
        else:
            photo.likes.remove(self.request.user)   
            response['liked'] = False        
        photo.save()
        return JsonResponse(response)


class FindUserAjax(TemplateView):
    def get(self, request, *args, **kwargs):
        if 'prefix' not in kwargs:
            return JsonResponse({'users': []})
        users = [
            {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            for user in User.objects.filter(
                username__startswith=kwargs['prefix'])[0:5]
        ]
        return JsonResponse({'users': users})
