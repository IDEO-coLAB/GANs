import numpy as np

width = 10
height = 10

def generate_image():
    img = np.random.random_integers(0, high=255, size=[10,10,4])
    fimg = list(img.flatten())
    fimg = [int(x) for x in fimg]
    return(fimg)

def get_size():
    return({"width": width, "height": height})
