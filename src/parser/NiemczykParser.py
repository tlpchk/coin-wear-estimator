from Parser import Parser
import re
import numpy as np
import pandas as pd
from utils import adj_grade_pattern

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
