from .utils import NIEMCZYK_DATASET_PATH, MARCINIAK_DATASET_PATH, metadata_path
from .parser.MarciniakParser import MarciniakParser
from .parser.NiemczykParser import NiemczykParser
import pandas as pd 

keyword = "Sztandar 1930"

for csv_path, parser in [(metadata_path(NIEMCZYK_DATASET_PATH), NiemczykParser), 
                         (metadata_path(MARCINIAK_DATASET_PATH), MarciniakParser)]:

    
    states_df = parser().get_df_with_states(keyword)
    meta_df = pd.read_csv(csv_path, sep='|')
    meta_df.drop(['title_state', 'description_state'], axis=1, errors='ignore', inplace=True)
    meta_df = meta_df.merge(states_df, how='left', on=['link'], copy=False)
    meta_df.to_csv(csv_path, sep='|', index=None)