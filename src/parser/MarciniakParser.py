from .Parser import Parser
import re
import numpy as np
import pandas as pd
from ..utils import adj_grade_pattern

class MarciniakParser(Parser):
    def __init__(self):
        super().__init__("marciniak")

    def extract_from_title(self, t):
        for method in [self.st_dot_method, self.grade_company_method]:
            s = method(t)
            if s:
                return s
    
    def extract_from_description(self, d):
        for method in [self.state_of_wear_method, self.inline_state_of_wear, self.grade_company_method]:
            s = method(d)
            if s:
                return s

    def inline_state_of_wear(self, d):
        pattern = re.compile("stan zachowania: ~?" + adj_grade_pattern)
        search = pattern.search(d)
        if not search:
            return
        condition = search.group(0)[17:].lstrip().rstrip("\\")
        return condition

    def add_missing_states(self, df):
        link_to_title_state = { \
            "https://aukcje.gndm.pl/pl/auction/1000066/id/566016/8610-5-zl-1930-sztandar-ms62": "NGC MS62", \
            "https://aukcje.gndm.pl/pl/auction/1000066/id/522080/1987-5-zl-1930-sztandar-3-3": "3/3+"}

        link_to_desc_state = { \
            'https://aukcje.gndm.pl/pl/auction/523/lot/2010/iirp-zestaw-5-zlotych-1930-sztandar-10' : '3+/2', \
            'https://aukcje.gndm.pl/pl/auction/1000066/id/644207/6431-sztandar-5-zlotych-1930-pcgs-au55': 'PCGS AU55', \
            'https://aukcje.gndm.pl/pl/auction/1000066/id/614519/8081-gleboki-sztandar-5-zl-1930-pcgs-au58-piekny': 'PCGS AU58', \
        }
        df = self.add_missing_states_from_dict(df, link_to_title_state, "title_state")
        df = self.add_missing_states_from_dict(df, link_to_desc_state, "description_state")
        return df
