from .Parser import Parser
import re
import numpy as np
import pandas as pd
from ..utils import adj_grade_pattern

class NiemczykParser(Parser):
    def __init__(self):
        super().__init__("niemczyk")

    def extract_from_title(self, title):
        for method in [self.st_dot_method, self.grade_company_method]:
            s = method(title)
            if s:
                return s
        
    def extract_from_description(self, d):
        for method in [self.state_of_wear_method, self.st_dot_method, self.grade_company_method]:
            s = method(d)
            if s:
                return s

    def add_missing_states(self, df):
        link_to_title_state = {"https://archiwum.niemczyk.pl/page/4883229206/ii-rp-5-zlotych-1930-sztandar-gleboki-st-32": "3+/2-"}
        link_to_desc_state = {'https://archiwum.niemczyk.pl/auction/14/300/ll-rp-5-zlotych-1930-sztandar-stempel-gleboki-srebro-ngc-ms62': 'NGC MS62', \
                              'https://archiwum.niemczyk.pl/auction/13/333/ii-rp-5-zlotych-1930-sztandar-stempel-gleboki-ngc-ms63': 'NGC MS63'}
        df = self.add_missing_states_from_dict(df, link_to_title_state, "title_state")
        df = self.add_missing_states_from_dict(df, link_to_desc_state, "description_state")
        return df