# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from lensapp.helpers import RandomFileName
from lensapp.ml.utils import get_sim_image_ids


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    birthdate = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=400, blank=True)
    following = models.ManyToManyField(User, related_name='followers')
    activated = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_user_profile, sender=User)


class Photo(models.Model):
    user = models.ForeignKey(User, related_name="uploaded_photos")
    path = models.ImageField(upload_to=RandomFileName('photos/user-photos/'))
    upload_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_photos")
    
    def __str__(self):
        return self.path.url

    def get_similar(self):
        sim_ids = get_sim_image_ids(self.path.url)
        return Photo.objects.filter(pk__in=sim_ids).all()
