from django.core.management.base import BaseCommand, CommandError
from django.core.files.uploadedfile import SimpleUploadedFile

from os import listdir
from os.path import isfile, join

from django.conf import settings

from lensapp.models import User, Photo

class Command(BaseCommand):
    def _read_images(self):
        path = settings.MEDIA_ROOT + '/photos/initial-photos/'
        return ['media/photos/initial-photos/' + f
                for f in listdir(path) if isfile(join(path, f))]
    
    def _get_file(self, filePath):
        file = open(filePath, 'rb')
        return SimpleUploadedFile(file.name, file.read())

    def handle(self, *args, **options):
        user_data = {
            'username': 'testuser',
            'email': 'test@test.com'
        }

        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(**user_data)
        else:
            user = User.objects.get(username=user_data['username'])

        if user.uploaded_photos.all().count() != 0:
            return
        paths = self._read_images()
        for path in paths:
            photo = Photo(path=self._get_file(path), user=user)
            photo.save()
