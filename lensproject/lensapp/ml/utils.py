import os
import pickle

from django.conf import settings

import numpy as np
from PIL import Image

def get_sim_image_ids(image_path):
    img = Image.open(settings.BASE_DIR + image_path)
    if img.size != settings.REQ_IMG_SIZE:
        img = img.resize(settings.REQ_IMG_SIZE)
    img_arr = np.expand_dims(np.array(img), axis=0)
    img.close()
    
    feature_map = settings.EXTRACT_IMAGE_FEATURES([img_arr])[0][0]

    index, distances = settings.INDEX.get_nns_by_vector(feature_map,
            6, search_k=-1, include_distances=True)

    return [i for i, d in list(zip(index, distances))[1:] if d < settings.TRESH]