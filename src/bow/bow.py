from src.utils import *
import numpy as np
from matplotlib import pyplot as plt
from tqdm.notebook import tqdm
import torch
from sklearn.model_selection import train_test_split
from silx.opencl import sift as silx_sift
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, f1_score
from src.utils import metadata_path, side_path, aligned_coins_path

if torch.cuda.is_available():
    from h2o4gpu.solvers import KMeans
else :
    from sklearn.cluster import KMeans

def getDescriptors(sift, img, sift_gpu):
    if sift_gpu:
      des = [kp.desc for kp in sift.keypoints(img, None)]
    else:
      kp, des = sift.detectAndCompute(img, None)
    return des

def clusterDescriptors(descriptors, no_clusters):
    kmeans = KMeans(n_clusters = no_clusters).fit(descriptors)
    return kmeans

def extractFeatures(kmeans, descriptor_list, no_clusters):
    lengths = [len(l) for l in descriptor_list]
    indices = kmeans.predict(np.vstack(descriptor_list))
    i = 0
    im_features = []
    for l in lengths:
        hist = np.histogram(indices[i:i+l], bins = np.arange(no_clusters+1))[0]
        im_features.append(hist)
        i = i + l
    return im_features

def normalizeFeatures(scale, features):
    return scale.transform(features)