from urllib.parse import urlparse, urlunparse, urlencode
from urllib.request import urlretrieve
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Scraper import Scraper

class NiemczykScraper(Scraper):
    def __init__(self):
        super().__init__("https://archiwum.niemczyk.pl", "niemczyk")

    def open_search_page(self, keyword: str, page = None):
        url = urlparse(self._base_url + "/search")
        params = {"search": keyword}
        if page:
            params['page'] = page
        url_new_query = urlencode(params)
        url_parsed = url._replace(query=url_new_query)
        url = urlunparse(url_parsed)
        self._driver.get(url)

    def get_list_of_coin_urls(self, keyword: str):
        driver = self._driver
        all_links = []
        wait = WebDriverWait(driver, 1)
        page = 1
        self.open_search_page(keyword, page)
        try:
            while wait.until(EC.visibility_of_element_located((By.ID, "post-data"))):
                page_links = list(map(lambda el : el.get_attribute("href"), driver.find_elements_by_xpath("//div[@id='post-data']//h3/a")))
                all_links += page_links
                page = page + 1
                self.open_search_page(keyword, page)
        except TimeoutException as error:
            print("Fetched {} links".format(len(all_links)))
        return all_links

    def scrap_coin_data_from_page(self, link):
        driver = self._driver
        driver.get(link)
        date = driver.find_element_by_xpath("//div[text()='Data sprzedaży:']/../div[2]").text
        title = driver.find_element_by_xpath("//div[@class='row']//h2/span[1]").text
        try:
            images = list(map(lambda el : el.get_attribute("href"), driver.find_elements_by_xpath("//div[@id='links']/a")))
        except Exception as e:
            images = []
        try: 
            desctiption = driver.find_element_by_xpath("//div[@class='tab-content']//div[@class='container']").text
        except Exception as e:
            desctiption = ""
        
        desctiption = desctiption.replace("\n","\\")
        return { "title": title, "date": date, "description": desctiption, "images": images, "link": link }