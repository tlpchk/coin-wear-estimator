import pandas as pd
from .utils import metadata_path, side_path, aligned_coins_path, master_coins_path, MARCINIAK_DATASET_PATH, NIEMCZYK_DATASET_PATH
from .grade_processing_utils import calculate_sheldon_and_categories
from bunch import Bunch
import h5py
import numpy as np
from tqdm.notebook import tqdm
import cv2
import itertools

def load_dataset(
    dataset_path=None,
    h5_path=None,
    categories=None,
    ds_shape=None,
    separate_sides=True,
    uncertain=False,
    string_columns=['y', 'name']
    ):
    
    if h5_path is not None:
        dataset = Bunch()
        with h5py.File(h5_path, 'r') as f:
            for k in f.keys():
                dataset[k] = np.array(f[k])
                if k in string_columns:
                    dataset[k] = dataset[k].astype('str')

        return dataset

    name2id = lambda name: int(name.split('_')[0])
    ds_name = "M" if "marciniak" in dataset_path else "N"
    
    if separate_sides:
        dataset = Bunch(X=[], y=[], side=[], name=[])
        label_tresh = 0
    else:
        dataset = Bunch(X=[], y=[], name=[])
        label_tresh = 0.2

    metadata_df = pd.read_csv(metadata_path(dataset_path), sep="|", index_col="id")
    metadata_df = calculate_sheldon_and_categories(metadata_df, uncertain=uncertain) # processed grade of the coin

    side_df = pd.read_csv(side_path(dataset_path), index_col="name")
    side_df = side_df[side_df["label"] > label_tresh] # coin is not unrelated data

    names = side_df.index.values
    names = [name for name in names if name2id(name) in metadata_df.index]  # coin have state defined


    if separate_sides:
        pbar = tqdm(total=len(names))

        for name in names:
            side = side_df.loc[name, "label"]
            if side > 0 and side < 1:
                side *= 10

            index = name2id(name)
            label = metadata_df.loc[index, "category"]

            im_path = "{}/{}".format(aligned_coins_path(dataset_path), name)
            im = cv2.imread(im_path)
            if ds_shape is not None:
                im = cv2.resize(im, ds_shape)

            dataset.X.append(im)
            dataset.y.append(label)
            dataset.name.append(ds_name+name)
            dataset.side.append(side)

            pbar.update(1)

    else:
        assert len(names) % 2 == 0
        pbar = tqdm(total=len(names)//2)
        for i in range(len(names)):
            if i % 2 == 1:
                continue
            assert name2id(names[i]) == name2id(names[i+1])
            
            name_side_dict = side_df.loc[[names[i], names[i+1]], "label"].to_dict()
            side_name_dict = dict(map(reversed, name_side_dict.items()))
            name_1, name_2 = side_name_dict[1], side_name_dict[2]
            index = name2id(name_1)
            label = metadata_df.loc[index, "category"]
            
            im_1 = cv2.imread("{}/{}".format(aligned_coins_path(dataset_path), name_1))
            im_2 = cv2.imread("{}/{}".format(aligned_coins_path(dataset_path), name_2))
            if ds_shape is not None:
                im_1 = cv2.resize(im_1, ds_shape)
                im_2 = cv2.resize(im_2, ds_shape)
            
            dataset.X.append((im_1, im_2))
            dataset.y.append(label)
            dataset.name.append(ds_name+str(index))

            pbar.update(1)

    pbar.close()
    return dataset

def to_h5(dataset, fileName, string_columns=['y', 'name']):
  with h5py.File(fileName, "w") as out:
    for k in dataset.keys():
      values = dataset[k]
      if k in string_columns:
          values = np.array(values).astype('S')
      out[k] = values

def join_datasets(datasets):
    new_dataset = Bunch()
    for k in datasets[0].keys():
        attr = list(itertools.chain.from_iterable([ ds[k] for ds in datasets]))
        new_dataset[k] = attr
    return new_dataset

def get_h5_name(separate_sides, uncertain):
  return "./{}_side_{}_categories.h5".format(
      "single" if separate_sides else "both",
      "5" if uncertain else "3",)