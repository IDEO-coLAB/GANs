import numpy as np
from PIL import Image
import hashlib

width = 10
height = 10
output_path = './public/imgs/'

def generate_image():
    img = np.random.random_integers(0, high=255, size=[10,10,3]).astype('uint8')
    # fimg = list(img.flatten())
    # fimg = [int(x) for x in fimg]
    hash = hashlib.sha1(img).hexdigest()
    hash = hash[:10]
    file_name = f'{hash}.jpg'
    Image.fromarray(img).save(f'{output_path}/{file_name}')
    return(file_name)

def get_size():
    return({'width': width, 'height': height})
