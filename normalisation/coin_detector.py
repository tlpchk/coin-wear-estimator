import numpy as np
import cv2
from matplotlib import pyplot as plt
import itertools
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter
import numpy as np

def create_circular_mask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask

def crop_coin(img_orig, height_img_ds=500, gb_size=(3,3), canny_th1=50, canny_th2=100, hough_param2=0.9, mc_size=(11, 11), method = 1 ):
    
    ds_ratio = 1
    if height_img_ds < img_orig.shape[0]:
        ds_ratio = height_img_ds/img_orig.shape[0]
        img_ds = cv2.resize(img_orig, None, fx=ds_ratio, fy=ds_ratio, interpolation=cv2.INTER_AREA) # downsampling
    else:
        img_ds = img_orig.copy()

    gray = cv2.cvtColor(img_ds, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, gb_size, 0)

    thresh = cv2.Canny(gray, canny_th1, canny_th2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, mc_size)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    if method == 2:
        _, th = cv2.threshold(closed, 1, 1, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(th, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        max_contour = max(contours, key=cv2.contourArea)
        img_max_contour = cv2.drawContours(np.zeros(gray.shape), max_contour, -1, (255,255,255), 1)

        closed = np.uint8(img_max_contour)

    for param2 in np.linspace(1, hough_param2, 10)[::-1]:
        print(param2)
        circles = cv2.HoughCircles(closed, cv2.HOUGH_GRADIENT, 1, minDist=img_ds.shape[0], param1=canny_th2, param2=param2, minRadius=int(0.35 * img_ds.shape[0]), maxRadius=int(0.5 * img_ds.shape[0]))
        if circles is not None:
            break

    circles = circles[0,:]
    (x, y, r) = max(circles, key=lambda c: c[2])
    x, y, r = x/ds_ratio, y/ds_ratio, r/ds_ratio

    masked_img = cv2.circle(closed, (int(x), int(y)), int(r), (0, 0, 255), 1)

    mask = create_circular_mask(img_orig.shape[0], img_orig.shape[1], center=(x,y), radius=r)
    masked_img = img_orig.copy()
    masked_img[~mask] = 0

    startY, endY = round(y-r), round(y+r)
    startX, endX = round(x-r), round(x-r) + (endY - startY)
    startY = max(startY, 0)
    startX = max(startX, 0)
    endY = min(masked_img.shape[0]-1, endY)
    endX = min(masked_img.shape[1]-1, endX)
    masked_img = masked_img[startY:endY, startX:endX]

    return masked_img