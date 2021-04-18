from .Parser import Parser
import re
import numpy as np
import pandas as pd
from utils import adj_grade_pattern

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
