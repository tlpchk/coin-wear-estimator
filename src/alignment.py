import cv2
from .image_utils import remove_illumination
import torch
import numpy as np
from tqdm.notebook import tqdm
import pandas as pd
from .detector import BACKGROUND_VALUE, create_circular_mask 
from .utils import cropped_coins_path, MARCINIAK_DATASET_PATH

from matplotlib import pyplot as plt
from scipy.spatial import distance
from silx.opencl import sift as silx_sift

REF_IMG_DICT = {
    1: cv2.imread(cropped_coins_path(MARCINIAK_DATASET_PATH)+ "/35_1.jpg"),
    2: cv2.imread(cropped_coins_path(MARCINIAK_DATASET_PATH)+ "/35_4.jpg"),
}

def align_with_reference(dst_im_orig,
                        src_im_orig,
                        ds_size = 800,
                        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False),
                        use_silx_sift=False,
                        maxIter=2000,
                        kernel_size=None,
                        name=None,
                        verbose=False
  ): 
    src_h = src_im_orig.shape[0]
    dst_h = dst_im_orig.shape[0]

    ds_size = min(ds_size, dst_h)
    ds_src_ratio = ds_size / src_h 
    ds_dst_ratio = ds_size / dst_h

    src_im = cv2.resize(src_im_orig, (ds_size, ds_size))
    dst_im = cv2.resize(dst_im_orig, (ds_size, ds_size))

    src_im = cv2.cvtColor(src_im, cv2.COLOR_BGR2GRAY)
    dst_im = cv2.cvtColor(dst_im, cv2.COLOR_BGR2GRAY)

    if kernel_size is not None:
        src_im = remove_illumination(src_im, kernel_size, 0)
        dst_im = remove_illumination(dst_im, kernel_size, 0)

#         src_gray = cv2.medianBlur(src_im, 5)
#         dst_gray = cv2.medianBlur(dst_im, 5)

#         src_gray = cv2.Canny(src_gray, 15, 30)
#         dst_gray = cv2.Canny(dst_gray, 15, 30)

    if verbose:
        fig, (ax1, ax2) = plt.subplots(1,2,figsize=(16,8))
        ax1.imshow(src_im, cmap='gray')
        ax2.imshow(dst_im, cmap='gray')
        plt.show()

    if use_silx_sift:
        sift = silx_sift.SiftPlan(template=src_im, devicetype="GPU" if torch.cuda.is_available() else "CPU")

        src_kp = sift.keypoints(src_im, None)
        src_des = np.asarray([p.desc for p in src_kp]).astype('float32')
        src_kp = [cv2.KeyPoint(x=p.x, y=p.y, _size=p.scale, _angle=np.rad2deg(p.angle)) for p in src_kp]

        dst_kp = sift.keypoints(dst_im, None)
        dst_des = np.asarray([p.desc for p in dst_kp]).astype('float32')
        dst_kp = [cv2.KeyPoint(x=p.x, y=p.y, _size=p.scale, _angle=np.rad2deg(p.angle)) for p in dst_kp]
    else:
        sift = cv2.SIFT_create()

        src_kp, src_des = sift.detectAndCompute(src_im, None)
        dst_kp, dst_des = sift.detectAndCompute(dst_im, None)


    matches = matcher.match(src_des, dst_des)
#     matches = sorted(matches, key = lambda x:x.distance)
#     matches = matches[:int(len(matches)*0.7)]
    matches = sorted(matches, key = lambda x: distance.euclidean( src_kp[x.queryIdx].pt , dst_kp[x.trainIdx].pt, src_h ))
    matches = matches[:len(matches)][:150]

    if verbose:
        plt.figure(figsize=(16,8))
        plt.imshow(cv2.drawMatches(
            src_im,
            src_kp,
            dst_im,
            dst_kp,
            matches,
            None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        )
        plt.show()

    MIN_MATCH_COUNT = 10
    
    src_pts = np.float32([ np.divide(src_kp[m.queryIdx].pt, ds_src_ratio) for m in matches ]).reshape(-1,1,2)
    dst_pts = np.float32([ np.divide(dst_kp[m.trainIdx].pt, ds_dst_ratio) for m in matches ]).reshape(-1,1,2)
    # M, inliers = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    M, inliers = cv2.estimateAffinePartial2D (src_pts, dst_pts, method=cv2.RANSAC, ransacReprojThreshold = 5.0,
        #confidence=0.99, 
        maxIters=2000
    )
    n_inliers = inliers.ravel().sum()

    tx = -int(M[0,2])
    ty = -int(M[1,2])
    scale = np.sqrt(M[1,0]**2 + M[0,0]**2)
    a = -np.arctan(M[1,0]/M[0,0])
    M_R = np.array([[np.cos(a), -np.sin(a), tx],\
                    [np.sin(a),  np.cos(a), ty]])

    new_h = int(src_h*scale)
    res_im = cv2.warpAffine(dst_im_orig, M_R, (new_h, new_h), borderValue=[BACKGROUND_VALUE]*3)

    mask = create_circular_mask(new_h, new_h)
    res_im[~mask] = 255

    if verbose:
        fig, (ax1, ax2) = plt.subplots(1,2,figsize=(16,8))
        ax1.imshow(np.uint8(cv2.resize(src_im_orig, (new_h, new_h)) * 0.5 + res_im * 0.5))
        ax2.imshow(res_im)
        plt.show()
    
    if n_inliers < MIN_MATCH_COUNT:
        w = n_inliers/len(matches)
        k = maxIter
        p = 1 - np.exp(k * np.log(1 - w ** 2))
        print("{} Warning: probability of success with obtained inlisers is {}".format(name, p))

    return res_im, n_inliers

def align_all_coins(csv_path, in_root, out_root, labels, inliers_csv, use_silx_sift):
    df = pd.read_csv(csv_path)
    # df["label"] = df["label"].astype("uint8")

    pbar = tqdm(total=len([l for l in df["label"] if l in labels]))

    for i, row in df.iterrows():
        name = row["name"]
        label = row["label"]
        if label not in labels:
            continue

        img = cv2.imread(in_root + "/" + name)
        if label > 0 and label < 1:
            label = label * 10 # align also images, that are not paired

        ref_im = REF_IMG_DICT[label]
        aligned, n_inliers = align_with_reference(img,
            ref_im,
            ds_size = 800,
            matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False),
            use_silx_sift=use_silx_sift,
            kernel_size=(61,61),
            name=name,
            verbose=False
        );
        cv2.imwrite(out_root + "/" + name, aligned)
        df.loc[i, "inliers"] = n_inliers
        df[['name', 'inliers']].to_csv(inliers_csv, index=None)

        pbar.update(1)
    
    pbar.close()