import cv2
from .detector import create_circular_mask, BACKGROUND_VALUE
import numpy as np

def remove_illumination(im, kernel_size, sigma=0):
    back = cv2.GaussianBlur(im, kernel_size, sigma)
    im = im.astype("float")
    im = np.subtract(im, back)
    im = im + np.mean(back)
    mask = create_circular_mask(im.shape[0], im.shape[1])
    im[~mask] = BACKGROUND_VALUE
    im[im < 0] = 0
    im[im > 255] = 255
    im = np.uint8(im)
    return im