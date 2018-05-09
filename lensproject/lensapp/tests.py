# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import json
import tempfile

from django.conf import settings

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.test import TestCase
from lensapp.forms import RegistrationForm, UploadPhotoForm
from lensapp.models import UserProfile, Photo

import lensapp.views

from captcha.models import CaptchaStore

from PIL import Image

class RegistrationTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@test.com',
            'password1': 'secret_discret',
            'password2': 'secret_discret',
        }

    def test_register(self):
        response = self.client.post('/register/', self.user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username=self.user_data['username']).exists())

        captcha_count = CaptchaStore.objects.count()
        
        self.failUnlessEqual(captcha_count, 1)
        captcha = CaptchaStore.objects.all()[0]
        self.user_data['captcha_0'] = captcha.hashkey
        self.user_data['captcha_1'] = captcha.response

        response = self.client.post('/register/', self.user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(
            User.objects.filter(username=self.user_data['username']).exists())
        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.uploaded_photos.count(), 0)
        self.assertEqual(user.profile.following.count(), 0)
        self.assertEqual(user.followers.count(), 0)

   
class LoginTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_login(self):
        # login
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertIn('_auth_user_id', self.client.session)

        # logout
        response = self.client.get('/logout/')
        self.assertNotIn('_auth_user_id', self.client.session)


class ImageCreator():
    @staticmethod
    def create_image():
        from PIL import Image
 
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')
 
        image = open(f.name, mode='rb')
        return SimpleUploadedFile(image.name, image.read())


class UploadPhotoTest(TestCase):
    def setUp(self):
        self.image = ImageCreator.create_image()
        self.photo_data = {
            'path': self.image
        }
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)
        self.client.post('/login/', self.credentials)
        self.user = User.objects.get(username=self.credentials['username'])
 
    def tearDown(self):
        self.image.close()

    def test_upload(self):
        # upload
        form = UploadPhotoForm(files=self.photo_data)
        self.assertTrue(form.is_valid())
        response = self.client.post('/upload_photo/',
                                    self.photo_data,
                                    follow=True)
        self.assertTrue(
            Photo.objects.filter(user=self.user).exists())

        photo = Photo.objects.get(pk=1)
        self.assertEqual(photo.user, self.user)
        self.assertEqual(photo.likes.count(), 0)

        # delete
        self.client.post('/photo/1/delete')
        self.assertFalse(
            Photo.objects.filter(user=self.user).exists())


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
        # follow
        response = self.client.get(
            '/ajax/follow_user/' + self.followed_credentials['username'] +'/', 
            follow=True
        )
        followed = User.objects.get(
            username=self.followed_credentials['username']
        )
        follower = User.objects.get(
            username=self.follower_credentials['username']
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', json.loads(response.content))
        self.assertTrue(followed in list(follower.profile.following.all()))
        self.assertTrue(follower.profile in list(followed.followers.all()))

        # follow user that does not exist
        response = self.client.get(
            '/ajax/follow_user/no_user/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', json.loads(response.content))

        # unfollow
        response = self.client.get(
            '/ajax/follow_user/' + self.followed_credentials['username'] + '/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', json.loads(response.content))
        self.assertFalse(followed in list(follower.profile.following.all()))
        self.assertFalse(follower.profile in list(followed.followers.all()))


class FeedTest(TestCase):
    def setUp(self):
        self.follower_credentials = {
            'username': 'follower',
            'password': 'secret'}
        self.followed_credentials = {
            'username': 'followed',
            'password': 'secret'}
        self.other_credentials = {
            'username': 'other',
            'password': 'secret'}
        self.follower = User.objects.create_user(**self.follower_credentials)
        self.followed = User.objects.create_user(**self.followed_credentials)
        self.other = User.objects.create_user(**self.other_credentials)

        self.image = ImageCreator.create_image()
        self.follower.profile.following.add(self.followed)
        Photo(path=self.image, user=self.followed).save()
        Photo(path=self.image, user=self.other).save()
        self.client.post('/login/', self.follower_credentials)

    def tearDown(self):
        self.image.close()

    def test_feed_view(self):
        response = self.client.get('/feed/')
        self.assertEqual(response.status_code, 200)
        photos = response.context['photos']
        self.assertEqual(photos.count(), 1)
        self.assertEqual(photos[0].user, self.followed)


class LikeTest(TestCase):
    def setUp(self):
        self.liker_credentials = {
            'username': 'liker',
            'password': 'secret'}
        self.uploader_credentials = {
            'username': 'uploader',
            'password': 'secret'}
        self.liker = User.objects.create_user(**self.liker_credentials)
        self.uploader = User.objects.create_user(**self.uploader_credentials)

        self.image = ImageCreator.create_image()
        self.photo = Photo(path=self.image, user=self.uploader)
        self.photo.save()
        self.client.post('/login/', self.liker_credentials)

    def tearDown(self):
        self.image.close()

    def test_like(self):
        # like
        response = self.client.get(
            '/ajax/like_photo/' + str(self.photo.pk) +'/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', json.loads(response.content))
        self.assertEqual(self.photo.likes.count(), 1)
        self.assertIn(self.liker, self.photo.likes.all())
        self.assertIn(self.photo, self.liker.liked_photos.all())

        # like photo that does not exist
        response = self.client.get(
            '/ajax/like_photo/2/', 
            follow=True
        )
        self.assertIn('error', json.loads(response.content))

        # unlike
        response = self.client.get(
            '/ajax/like_photo/' + str(self.photo.pk) +'/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('error', json.loads(response.content))
        self.assertEqual(self.photo.likes.count(), 0)
        self.assertNotIn(self.liker, self.photo.likes.all())
        self.assertNotIn(self.photo, self.liker.liked_photos.all())

class FindUsersTest(TestCase):
    def setUp(self):
        self.users = []
        for i in range(0, 5):
            user_credentials = {
                'username': 'user' + str(i),
                'password': 'secret',
                'first_name': 'test',
                'last_name': 'test',
            }
            self.users = self.users + [
                User.objects.create_user(**user_credentials)
            ]

    def test_not_found(self):
        response = self.client.get(
            '/ajax/find_user/' + 'no_user' +'/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        responseDict = json.loads(response.content)
        self.assertIn('users', responseDict)
        self.assertEqual(len(responseDict['users']), 0)

    def test_found(self):
        response = self.client.get(
            '/ajax/find_user/' + 'user' +'/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        responseDict = json.loads(response.content)
        self.assertIn('users', responseDict)
        self.assertEqual(len(responseDict['users']), 5)
        for user in self.users:
            self.assertIn({
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }, responseDict['users'])


    def test_unique_found(self):
        response = self.client.get(
            '/ajax/find_user/' + 'user2' +'/', 
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        responseDict = json.loads(response.content)
        self.assertIn('users', responseDict)
        self.assertEqual(len(responseDict['users']), 1)
        self.assertIn({
            'username': 'user2',
            'first_name': 'test',
            'last_name': 'test'
        }, responseDict['users'])


