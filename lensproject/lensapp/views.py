# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView

from lensapp.forms import RegistrationForm
from lensapp.models import UserProfile, User

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

