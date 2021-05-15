import numpy as np
from .utils import basic_grading_dict, get_shaldon_value

def coins_with_no_grade(df):
    df = df[df["title_state"].isna() & df["description_state"].isna()]
    return df 

def coins_with_ambiguity(df):
    df = df[df["title_state"].str.replace(" ","") != df["description_state"].str.replace(" ","")]
    df = df[df["title_state"].notna() & df["description_state"].notna()]
    return df

def unify_states(df):
    df = df[~df.index.isin(coins_with_no_grade(df).index)]
    df = df[~df.index.isin(coins_with_ambiguity(df).index)]
    df["state"] = df["title_state"]
    df.loc[df["state"].isna(), "state"] = df["description_state"]
    df.drop(["description_state", "title_state"], axis=1, inplace = True)
    return df

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def get_nearest_category_value(grade, categories=["1", "2", "3"]):
    basic_grading_dict_inv = {v: k for k, v in basic_grading_dict.items()}
    categories_in_sheldon = [basic_grading_dict[cat] for cat in categories]
    nearest_sheldon_value = find_nearest(categories_in_sheldon, grade)
    return basic_grading_dict_inv[nearest_sheldon_value]
    
def get_circulate_category(grade):
    if grade >= 60:
        return "1"
    elif grade >= 50:
        return "2"
    else:
        return "3"

def calculate_sheldon_and_categories(df, categories=["1","1-","2","2-","3"]):
    df = unify_states(df)
    df["sheldon"] = df["state"].apply(get_shaldon_value)
    # df["category"] = df["sheldon"].apply(lambda grade: get_nearest_category_value(grade, categories))
    df["category"] = df["sheldon"].apply(lambda grade: get_circulate_category(grade))
    return df