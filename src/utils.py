import sys

def get_filename(keyword):
    return keyword.lower().replace(" ","_")

# https://www.ngccoin.com/specialty-services/ancient-coins/grading.aspx
NGC_grading = {
"PR"	:	1,
"FA"	:	2,
"AG"	:	3,
"G"	    :	5,  
"VG"	:   9,  
"F"	    :	12,
"Ch F"	:	15,
"VF"	:   23,  
"Ch VF"	:   33,  
"XF"	:	40,
"Ch XF"	:	45,
"AU"	:   52,	
"Ch AU"	:   57,  
"MS"	:   61,	
"Ch MS"	:	63, 
"Gem MS":	68,  
}

# https://www.facebook.com/gndmpl/posts/1111724668975411/
# https://goldco.pl/blog/grading-monet-ocena-stanu-zachowania-monet/#:~:text=Najbardziej%20po%C5%BC%C4%85dane%20monety%20to%20te,wyst%C4%99puj%C4%85%20w%20najwy%C5%BCszych%20stanach%20zachowania.
basic_grading = {
    "L" : 70, 
    "L-": 67,
    "1" : 65,
    "1-": 61,
    "2+": 58,
    "2" : 52,
    "2-": 45,
    "3+": 42,
    "3" : 35,
    "3-": 25,
    "4+": 15,
    "4" : 12,
    "4-": 11,
    "5+": 10,
    "5" : 6,
    "5-": 4,
}

adj_grade_pattern = "[12345L][+-]?(/[12345L][+-]?)?"
companies = ["GCN", "NGC", "PCGS"]
grade_prefixes = ["UNC", "PF", "MS", "AU", "XF", "VF"]
company_grade_pattern = "(%s) (%s)\s?(\d{2})?" % ("|".join(companies), "|".join(grade_prefixes))

NIEMCZYK = "niemczyk"
MARCINIAK = "marciniak"

if 'google.colab' in sys.modules:
    ROOT_PATH = "/content/drive/MyDrive/coin-wear-estimator"
else:
    ROOT_PATH = "/Users/telepchuk/PWr/Dan III/Magister/coin-wear-estimator"

KEYWORD = "Sztandar 1930"
MARCINIAK_DATASET_PATH = "{}/data/marciniak/{}".format(ROOT_PATH, get_filename(KEYWORD))
NIEMCZYK_DATASET_PATH = "{}/data/niemczyk/{}".format(ROOT_PATH, get_filename(KEYWORD))

metadata_path = lambda ds_path: ds_path + "/csv/metadata.csv"
page_link_path = lambda ds_path: ds_path + "/csv/page_link.csv"
side_path = lambda ds_path: ds_path + "/csv/side.csv"
size_aligned_path = lambda ds_path: ds_path + "/csv/size_aligned.csv"

aligned_coins_path = lambda ds_path, : ds_path + "/img/aligned"
cropped_coins_path = lambda ds_path: ds_path + "/img/cropped"
master_coins_path = lambda ds_path: ds_path + "/img/master"
raw_coins_path = lambda ds_path: ds_path + "/img/raw"
