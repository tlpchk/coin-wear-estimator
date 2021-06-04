from .scraper.MarciniakScraper import MarciniakScraper 
from .scraper.NiemczykScraper import NiemczykScraper 
import sys

# keyword = "Sztandar 1930"
# keyword = "Piłsudski 1939"
keyword = sys.argv[1]
download_links = False 

niemczyk = NiemczykScraper()
niemczyk.pipeline(keyword, download_links=download_links)

marciniak = MarciniakScraper()
marciniak.pipeline(keyword, download_links=download_links)