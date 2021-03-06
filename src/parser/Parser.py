import pandas as pd
from abc import ABC, abstractmethod
import re
import numpy as np
from ..utils import adj_grade_pattern, company_grade_pattern, ROOT_PATH, get_filename

class Parser(ABC):
    def __init__(self, name):
        self._name = name

    @abstractmethod
    def extract_from_title(self, t):
        pass

    @abstractmethod
    def extract_from_description(self, d):
        pass

    @abstractmethod
    def add_missing_states(self, df):
        pass

    def get_df(self, keyword, images_only=True):
        df = pd.read_csv("{}/data/{}/{}/csv/metadata.csv".format(ROOT_PATH, self._name, get_filename(keyword)), sep="|")
        if images_only:
            df = df[df['images'] != '[]']
        return df

    def st_dot_method(self, title):
        compile = re.compile("(s|S)t\.\s?~?" + adj_grade_pattern)
        search = compile.search(title)
        if not search:
            return
        condition = search.group(0)[3:].lstrip()
        return condition

    def state_of_wear_method(self, d):
        pattern = "\\\\Stan zachowania:? ((~?{})|{})".format(adj_grade_pattern, company_grade_pattern)
        compile = re.compile(pattern)
        search = compile.search(d)
        if not search:
            return
        condition = search.group(0)[17:].lstrip().rstrip("\\")
        return condition
  
    def grade_company_method(self, d):
        compile = re.compile(company_grade_pattern)
        search = compile.search(d)
        if not search:
            return
        condition = search.group(0)
        return condition

    def get_df_with_states(self, keyword):
        df = self.get_df(keyword) 

        t_states = []
        d_states = []

        for i, row in df[["title", "description"]].iterrows():
            t = row["title"]
            d = row["description"]
            t_state = self.extract_from_title(t) 
            
            if pd.isnull(d):
                d_state = None
            else:
                d_state = self.extract_from_description(d)
                
            if not t_state:
                t_state = np.nan
            if not d_state:
                d_state = np.nan
            t_states.append(t_state)
            d_states.append(d_state)

        df["title_state"] = t_states
        df["description_state"] = d_states

        df = self.add_missing_states(df)

        return df[["link", "title_state", "description_state"]]

    def add_missing_states_from_dict(self, df, link_to_state, attr):
        df_copy = df.copy()
        for link, state in link_to_state.items():
            rows_match_link = df["link"] == link
            df_copy.loc[rows_match_link, attr] = state
        return df_copy
