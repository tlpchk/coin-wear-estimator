from .detector import crop_all_coins
from .utils import side_path,raw_coins_path,cropped_coins_path,  MARCINIAK_DATASET_PATH, NIEMCZYK_DATASET_PATH
import os

for ds_path in [MARCINIAK_DATASET_PATH, NIEMCZYK_DATASET_PATH]:
    if not os.path.exists(cropped_coins_path(ds_path)):
        os.makedirs(cropped_coins_path(ds_path))
    crop_all_coins(side_path(ds_path),
                raw_coins_path(ds_path),
                cropped_coins_path(ds_path))
