from .scraper.MarciniakScraper import MarciniakScraper 
from .scraper.NiemczykScraper import NiemczykScraper 

keyword = "Sztandar 1930"
download_links = True 

niemczyk = NiemczykScraper()
niemczyk.pipeline(keyword, download_links=download_links)

marciniak = MarciniakScraper()
marciniak.pipeline(keyword, download_links=download_links)