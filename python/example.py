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
zsize = 16 # number of variables for "genome"

model = M(None, batch_size=batch_size, img_shape=img_shape, checkpoints_path=checkpoints_path, zsize=zsize)
model.build_model()
model.setup_session()

def generate_image():
    zdraw = np.random.normal(scale=1.0, size=(batch_size, zsize)).astype('float32')
    imgs = pixels01(model.Gz.eval(
        { model.Z: zdraw, model.is_training: False },
        session=model.sess))
    img = imgs[0,:,:,:]
    hash = hashlib.sha1(img).hexdigest()
    hash = hash[:10]
    file_name = f'{hash}.jpg'
    img_asints = (img * 255.0).astype('uint8')
    Image.fromarray(img_asints).save(f'{output_path}/{file_name}')
    return(file_name)

def get_size():
    return({'width': img_shape, 'height': img_shape})
