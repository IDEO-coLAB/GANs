import tensorflow as tf
import numpy as np
import math
from PIL import Image
import hashlib

from utils import pixels01
from model import Model as M

# Setup
checkpoints_path = '/Users/alukasik/Documents/IDEO/Developer/checkpoints/chairs-30-5-18/checkpoint.ckpt'
output_path = './public/imgs/'
batch_size = 64 # must match batch size of saved session
img_shape = (256, 256)
similar_chair_delta = 0.6
zsize = 16 # number of variables for "genome"

model = M(None, batch_size=batch_size, img_shape=img_shape, checkpoints_path=checkpoints_path, zsize=zsize)
model.build_model()
model.setup_session()

def name_save_chair(img):
    hash = hashlib.sha1(img).hexdigest()
    hash = hash[:10]
    file_name = f'{hash}.jpg'
    img_asints = (img * 255.0).astype('uint8')
    Image.fromarray(img_asints).save(f'{output_path}/{file_name}')
    return file_name

def generate_images_latent_vectors(zvector):
    imgs = pixels01(model.Gz.eval(
        { model.Z: zvector, model.is_training: False },
        session=model.sess))
    return imgs

def generate_random_chair():
    zdraw = np.random.normal(scale=1.0, size=(batch_size, zsize)).astype('float32')
    imgs = generate_images_latent_vectors(zdraw)
    img = imgs[0,:,:,:]
    file_name = name_save_chair(img)
    string_latent_vector = stringify_latent_vector(zdraw[0,:])
    return {'file_name': file_name, 'latent_vector': string_latent_vector}

def generate_similar_chairs(string_latent_vector):
    y = string_latent_vector.split(',')
    unpacked = [float(x) for x in y]
    latent_vector = np.array(unpacked)
    varied = latent_vector + np.random.normal(scale=similar_chair_delta, size=(8, zsize)).astype('float32')
    imgs = generate_images_latent_vectors(varied)
    file_names = [name_save_chair(x) for x in imgs]
    string_latent_vectors = [stringify_latent_vector(x) for x in list(varied)]
    return {'file_names': file_names, 'latent_vectors': string_latent_vectors}

def stringify_latent_vector(zvector):
    # we are just taking the two most significant digits, rounding them and sending them to the browser
    rounded = np.round(zvector, 2)
    packed = [str(x) for x in rounded]
    genome = ','.join(packed)
    return genome

def get_size():
    return({'width': img_shape, 'height': img_shape})
