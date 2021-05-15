from .alignment import align_all_coins
from .utils import NIEMCZYK_DATASET_PATH, MARCINIAK_DATASET_PATH, aligned_coins_path, cropped_coins_path, side_path, inliers_path
import os 

for ds_path in [NIEMCZYK_DATASET_PATH, MARCINIAK_DATASET_PATH]:
    if not os.path.exists(aligned_coins_path(ds_path)):
        os.makedirs(aligned_coins_path(ds_path))
    align_all_coins(
        side_path(ds_path),
        cropped_coins_path(ds_path),
        aligned_coins_path(ds_path),
        [0.1, 0.2, 1, 2],
        inliers_csv=inliers_path(ds_path),
        use_silx_sift=False
    )