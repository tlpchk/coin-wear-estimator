from src.utils import *
import numpy as np
import cv2
from matplotlib import pyplot as plt
from tqdm.notebook import tqdm
import torch
from sklearn.model_selection import train_test_split
from silx.opencl import sift as silx_sift
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score
from src.utils import metadata_path, side_path, aligned_coins_path


def paramSelection(X, y, estimator, param_grid, nfolds):
    grid_search = GridSearchCV(estimator, param_grid, cv=nfolds, scoring='f1_weighted', n_jobs=-1)
    grid_search.fit(X, y)
    grid_search.best_params_
    return grid_search.best_params_

def optimize_model(features, train_labels, estimatorClass, param_grid):
    params = paramSelection(features, train_labels, estimatorClass(), param_grid, 5)

    print(params)
    model = estimatorClass(**params)
    model.fit(features, train_labels)
    return model
