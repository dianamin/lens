# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase
from lensapp.forms import RegistrationForm, UploadPhotoForm
from lensapp.models import UserProfile, Photo


class RegistrationTest(TestCase):
    def setUp(self):
        self.user_data = {
        	'username': 'testuser',
        	'first_name': 'test',
        	'last_name': 'test',
        	'email': 'test@test.com',
        	'password1': 'secret_discret',
        	'password2': 'secret_discret'
        }

    def test_register(self):
    	form = RegistrationForm(data=self.user_data)
    	self.assertTrue(form.is_valid())
    	form.save()

    	self.assertTrue(
    		User.objects.filter(username=self.user_data['username']).exists())
    	user = User.objects.filter(username=self.user_data['username'])
    	self.assertTrue(UserProfile.objects.filter(user=user).exists())

        	
class LoginTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_login(self):
    	#login
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)

        #logout
        response = self.client.get('/logout/')
        self.assertFalse(response.context['user'].is_active)


class UploadPhotoTest(TestCase):
    def setUp(self):
        self.photo_data = {
            'path': 'path'
        }
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)
        self.client.post('/login/', self.credentials, follow=True)

    def test_upload(self):
    	form = UploadPhotoForm(data=self.photo_data)
    	self.assertTrue(form.is_valid())
    	response = self.client.post('/upload_photo/', self.photo_data)
    	self.assertTrue(
    		Photo.objects.filter(path=self.photo_data['path']).exists()
    	)


class FollowTest(TestCase):
    def setUp(self):
        self.follower_credentials = {
            'username': 'follower',
            'password': 'secret'}
        self.followed_credentials = {
            'username': 'followed',
            'password': 'secret'}
        User.objects.create_user(**self.follower_credentials)
        User.objects.create_user(**self.followed_credentials)
        self.client.post('/login/', self.follower_credentials, follow=True)

    def test_follow(self):
    	#follow
        self.client.get(
        	'/ajax/follow_user/' + self.followed_credentials['username'] +'/', 
        	follow=True
        )
        followed = User.objects.get(
        	username=self.followed_credentials['username']
       	)
        follower = User.objects.get(
        	username=self.follower_credentials['username']
       	)
       	self.assertTrue(followed in list(follower.profile.following.all()))
       	self.assertTrue(follower.profile in list(followed.followers.all()))

       	#unfollow
        self.client.get(
        	'/ajax/follow_user/' + self.followed_credentials['username'] +'/', 
        	follow=True
        )
       	self.assertFalse(followed in list(follower.profile.following.all()))
       	self.assertFalse(follower.profile in list(followed.followers.all()))

