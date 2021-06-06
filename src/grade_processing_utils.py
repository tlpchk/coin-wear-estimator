import numpy as np
from .utils import basic_grading_dict, get_shaldon_value, basic_grading

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

def find_nearest_idx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def get_nearest_category_value(sheldon, state, categories=["1", "1/2", "2", "2/3", "3"]):
    if expert_grading(state) is not None:
        return get_circulate_category(sheldon)
    categories_in_sheldon = [basic_grading(cat) for cat in categories
    nearest_category_idx = find_nearest_idx(categories_in_sheldon, grade)
    return categories[nearest_category_idx]
    
def get_circulate_category(sheldon):
    if sheldon >= 60:
        return "1"
    elif sheldon >= 50:
        return "2"
    else:
        return "3"

def uncertain_categories(sheldon, state):
    categories = {
        "1.5": ['1-/2', '1-/2+', '2+/1-'], # [56.5, 59.5] ,#
        "2.5": ['2-', '2-/3', '2-/3+', '2/2-', '2/3', '3+/2', '3+/2-', '3/2', '~3+/2', '~3+/2-'] #[45, 40, 43.5, 48.5, 47]
    }
    for k,v in categories.items():
        if state in v:
            return k
    
    return get_circulate_category(sheldon)


def calculate_sheldon_and_categories(df, uncertain=False):
    df = unify_states(df)
    df["sheldon"] = df["state"].apply(get_shaldon_value)
    if uncertain:
        # df["category"] = df[["sheldon", "state"]].apply(lambda row: uncertain_categories(row[0], row[1]), axis=1 )
        df["category"] = df[["sheldon", "state"]].apply(lambda row: get_nearest_category_value(row[0], row[1]), axis=1)
    else:
        df["category"] = df["sheldon"].apply(lambda grade: get_circulate_category(grade))
    return df