from src.utils import *
import numpy as np
import cv2
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
from sklearn.metrics import f1_score
from src.utils import metadata_path, side_path, aligned_coins_path


def svcParamSelection(X, y, nfolds):
    Cs = [1.1, 0.9, 0.7, 0.5, 0.3, 0.1]
    n_features = len(X[0])
    gammas = [0.2, 0.1, 1/n_features, 2/n_features, 1/(2*n_features)]
    kernel = ['linear', 'poly', 'rbf', 'sigmoid']
    param_grid = {'C': Cs, 'kernel': kernel, 'gamma': gammas}
    
    # SVC(kernel=kernel)
    grid_search = GridSearchCV(SVC(kernel=kernel), param_grid, cv=nfolds, scoring='f1_weighted')
    grid_search.fit(X, y)
    grid_search.best_params_
    return grid_search.best_params_

def optimize_svm(im_features, train_labels):
    features = im_features
    
    params = svcParamSelection(features, train_labels, 5)
    # C_param, gamma_param = params.get("C"), params.get("gamma")
    # print(C_param, gamma_param)
    # svm = SVC(kernel = kernel, C =  C_param, gamma = gamma_param, class_weight = 'balanced')

    C_param, kernel_param, gamma_param = params.get("C"), params.get("kernel"), params.get("gamma")
    print(C_param, kernel_param, gamma_param)
    svm = SVC(kernel = kernel_param, C = C_param, gamma=gamma_param, class_weight = 'balanced')

    svm.fit(features, train_labels)
    return svm
