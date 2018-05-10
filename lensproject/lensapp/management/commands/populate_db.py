from django.core.management.base import BaseCommand, CommandError
from django.core.files.uploadedfile import SimpleUploadedFile

from os import listdir
from os.path import isfile, join

from django.conf import settings

from lensapp.models import User, Photo

from PIL import Image
from annoy import AnnoyIndex
import numpy as np
from tqdm import tqdm

np.random.seed(7)

class Command(BaseCommand):

    def _read_images(self):
        path = settings.SEED_IMAGES_ROOT
        return ['seed_images/' + f
                for f in listdir(path) if isfile(join(path, f))]
    
    def _get_file(self, filePath):
        file = open(filePath, 'rb')
        return SimpleUploadedFile(file.name, file.read())

    def create_index_file(self):
        NUM_TREES = 100
        IMAGES_SIZE = (256, 256)
        BATCH_SIZE = 64

        file_paths, image_ids = list(zip(
            *[(photo.path, photo.pk) for photo in Photo.objects.all()]))

        print('Reading images')
        images = np.zeros((len(file_paths),
                IMAGES_SIZE[0], IMAGES_SIZE[1], 3))

        for i, fp in enumerate(file_paths):
            img = Image.open(fp)
            if img.size != IMAGES_SIZE:
                img = img.resize(IMAGES_SIZE)
            images[i] = np.array(img)
            img.close()

        images = np.split(images,
                np.arange(BATCH_SIZE, images.shape[0], BATCH_SIZE))

        print('Extracting features')
        feature_vectors = []
        for images_batch in tqdm(images):
            feature_vectors.append(settings.EXTRACT_IMAGE_FEATURES \
                    ([images_batch])[0])
        feature_vectors = np.concatenate(feature_vectors, axis=0)

        print('Building index')
        index = AnnoyIndex(settings.INDEX_VECTORS_SIZE)
        for f, iid in tqdm(zip(feature_vectors, image_ids)):
            index.add_item(iid, f)
        index.build(NUM_TREES)

        print('Saving Index')
        index.save(settings.INDEX_PATH)

    def get_user_data(self, user_id):
        return {
            'username': 'testuser%s' % user_id,
            'email': 'test%s@test.com' % user_id,
            'first_name': 'Test %s' % user_id,
            'last_name': 'User'
        }

    def handle(self, *args, **options):
        NUM_USERS = 15

        print('Creat or reset users')
        users = []
        for i in range(NUM_USERS):
            user_data = self.get_user_data(i)
            if not User.objects.filter(username=user_data['username'])\
                    .exists():
                user = User.objects.create_user(**user_data)
            else:
                user = User.objects.get(username=user_data['username'])

            if user.uploaded_photos.all().count() != 0:
                user.uploaded_photos.all().delete()

            user.set_password('testuser')
            user.save()
            users.append(user)

        print('Uploading images')
        paths = self._read_images()[:200]
        np.random.shuffle(paths)
        for i, path in enumerate(paths):
            photo = Photo(path=self._get_file(path), user=users[i%NUM_USERS])
            photo.save()

        self.create_index_file()
