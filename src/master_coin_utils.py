
from src.detector import BACKGROUND_VALUE
import numpy as np
import cv2
import numpy as np
import pandas as pd
from src.utils import *
import pandas as pd
from .image_utils import remove_illumination
from tqdm.notebook import tqdm
from bunch import Bunch

def get_design_mask(master_coin, canny_l=14, cann_u=30):
    mask = master_coin.copy()
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    mask = cv2.medianBlur(mask, 3)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4,4))
    mask = cv2.dilate(mask, kernel ,iterations = 1)

    mask = remove_illumination(mask, (61,61), 0)

    mask = cv2.Canny(mask, canny_l, cann_u)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    mask = cv2.dilate(mask, kernel ,iterations = 3)

    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2))
    # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def generate_general_master_coin(label):
    array_df_size = []
    array_df_side = []
    for ds_path in [MARCINIAK_DATASET_PATH, NIEMCZYK_DATASET_PATH]: 
        df = pd.read_csv(size_aligned_path(ds_path))
        df["name"] = df["name"].apply(lambda x: aligned_coins_path(ds_path) + "/" + x)
        array_df_size.append(df)

        df =  pd.read_csv(side_path(ds_path))
        df["name"] = df["name"].apply(lambda x: aligned_coins_path(ds_path) + "/" + x)
        array_df_side.append(df)

    df_size = pd.concat(array_df_size)
    df_side = pd.concat(array_df_side)

    df = df_size.merge(df_side, how='inner', on='name')
    df = df.sort_values(by=['size'], ascending=False)
    df = df[df["label"] == label]
    names = df["name"]
    stack = np.stack([cv2.resize(cv2.imread(name), (700,700)) for name in names])
    master_coin = np.uint8(np.mean(stack, axis=0))

    return master_coin

def get_wear_marks(coin, design_mask, ds_shape=None, canny_l=None, canny_u=None):
    if ds_shape is not None:
        coin = cv2.resize(coin, ds_shape)
    if canny_l is not None:
        coin = cv2.cvtColor(coin, cv2.COLOR_BGR2GRAY)
        coin = cv2.medianBlur(coin, 3)
        # coin = cv2.GaussianBlur(coin, (3,3), 0.5)
        coin = cv2.Canny(coin, canny_l, canny_u)
        coin = np.multiply(~design_mask.astype(bool), coin)
    else:
        design_mask = np.repeat(design_mask[:, :, np.newaxis], 3, axis=2)
        coin = coin.copy()
        coin[design_mask.astype(bool)] = BACKGROUND_VALUE
    return coin

def convert_to_wear_marks_dataset(dataset, separate_sides, ds_shape=None, canny_l=150, canny_u=200):
    dataset = Bunch(dataset.copy())
    master_coin_dict = { \
        1: cv2.imread(master_coins_path(MARCINIAK_DATASET_PATH) + "/1_general.jpg"), \
        2: cv2.imread(master_coins_path(MARCINIAK_DATASET_PATH) + "/2_general.jpg"), \
    }
    design_mask_dict = { \
        1: get_design_mask(master_coin_dict[1]), \
        2: get_design_mask(master_coin_dict[2]), \
    }

    X = []
    n = len(dataset.X)
    pbar = tqdm(total=n)
    for i in range(n):
        if separate_sides:
            side = dataset.side[i]
            wear_marks = get_wear_marks(dataset.X[i], design_mask_dict[side], ds_shape=ds_shape, canny_l=canny_l, canny_u=canny_u)
            X.append(wear_marks)
        else:
            wear_marks_1 = get_wear_marks(dataset.X[i][0], design_mask_dict[1], ds_shape=ds_shape, canny_l=canny_l, canny_u=canny_u)
            wear_marks_2 = get_wear_marks(dataset.X[i][1], design_mask_dict[2], ds_shape=ds_shape, canny_l=canny_l, canny_u=canny_u)
            X.append((wear_marks_1, wear_marks_2))
        pbar.update(1)
    
    # wear_marks_dataset = Bunch()
    # for k in dataset.keys():
    #     wear_marks_dataset[k] = dataset.k
    # wear_marks_dataset.X = X

    dataset.X = X
    pbar.close()  

    return dataset
