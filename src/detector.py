import numpy as np
import cv2
from matplotlib import pyplot as plt
import itertools
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter
import numpy as np
import pandas as pd
from tqdm import tqdm
from silx.opencl import sift as silx_sift

BACKGROUND_VALUE = 255

class BriefDetector():
  def __init__(self):
    self.detector = cv2.xfeatures2d.StarDetector_create()
    self.extractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()
  
  def detectAndCompute(self, image, kp):
    kp = self.detector.detect(image, kp)
    des = self.extractor.compute(image, kp)
    if des is None:
        des = np.zeros((1, 32), dtype='float32')
    return des

class SiftGPUDetector():
    def __init__(self, template):
        separate_sides = template.shape[0] != 2 
        if not separate_sides:
            template=X[0]
        
        self.extractor = silx_sift.SiftPlan(template=template, devicetype="GPU")
  
    def __init__(self, shape=(700, 700, 3), dtype='uint8'):        
        self.extractor = silx_sift.SiftPlan(shape=shape, dtype='uint8', devicetype="GPU")
    
    def detectAndCompute(self, image, compute_kp=None):
        keypoints = self.extractor.keypoints(image, None)
        kp = []
        if compute_kp is not None:
          kp = [cv2.KeyPoint(x=p.x, y=p.y, _size=p.scale, _angle=np.rad2deg(p.angle)) for p in keypoints]
        des = [p.desc for p in keypoints]
        return kp, des

def create_circular_mask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

    mask = dist_from_center <= radius
    return mask

def crop_coin(img_orig, height_img_ds=800, gb_size=(3,3), canny_th1=40, canny_th2=100, hough_param2=1, mc_size=(11, 11), method = 1):
    ds_ratio = height_img_ds/img_orig.shape[0]
    img_ds = cv2.resize(img_orig, None, fx=ds_ratio, fy=ds_ratio, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img_ds, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, gb_size, 0)

    thresh = cv2.Canny(gray, canny_th1, canny_th2)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, mc_size)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.GaussianBlur(closed, gb_size, 0)

    circles = cv2.HoughCircles(closed, cv2.HOUGH_GRADIENT, 1, minDist=img_ds.shape[0], param1=canny_th2, param2=hough_param2, minRadius=int(0.35 * img_ds.shape[0]), maxRadius=int(0.5 * img_ds.shape[0]))

    circles = circles[0,:]
    (x, y, r) = max(circles, key=lambda c: c[2])
    x, y, r = x/ds_ratio, y/ds_ratio, r/ds_ratio


    mask = create_circular_mask(img_orig.shape[0], img_orig.shape[1], center=(x,y), radius=r)
    masked_img = img_orig.copy()
    masked_img[~mask] = BACKGROUND_VALUE

    startY = max(round(y-r), 0)
    startX = max(round(x-r), 0)
    endY = min(masked_img.shape[0]-1, round(y+r))
    endX = min(masked_img.shape[1]-1, round(x+r))
    size = min(endY - startY, endX - startX)
    endY = startY + size
    endX = startX + size
    
    masked_img = masked_img[startY:endY, startX:endX]

    return masked_img

def crop_all_coins(csv_path, image_in_path, image_out_path):
    df = pd.read_csv(csv_path)
    names = df[df["label"] > 0]["name"]
    pbar = tqdm(total=len(names))

    for name in names:
        try:
            img = cv2.imread(image_in_path + "/" + name)
            crop = crop_coin(img)
            cv2.imwrite(image_out_path +"/" + name, crop)
        except:
            print('error')
            pass
        pbar.update(1)
    pbar.close()