from urllib.parse import urlparse, urlunparse, urlencode
from urllib.request import urlretrieve
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Scraper import Scraper

class MarciniakScraper(Scraper):
    def __init__(self):
        super().__init__("https://aukcje.gndm.pl/pl/archive", "marciniak")

    def open_search_page(self, keyword: str, page = 1):
        url = urlparse("{}/{}/0/0/0/{}".format(self._base_url, page, keyword))
        url = urlunparse(url)
        self._driver.get(url)


    def get_list_of_coin_urls(self, keyword: str):
        driver = self._driver
        all_links = []
        page = 1
        wait = WebDriverWait(driver, 3)
       
        while True:
            self.open_search_page(keyword, page)
            i = 1
            try:
                while wait.until(EC.visibility_of_element_located((By.ID, "scrollpart" + str(i)))):
                    scrollpart_links = list(map(lambda el : el.get_attribute("href"),
                                                driver.find_elements_by_xpath("//div[@id='scrollpart{}']//a[@class='title']".format(i))
                                                ))
                    all_links += scrollpart_links
                    self.scroll_to_bottom()
                    i = i + 1
            except TimeoutException as error:
                if i != 11:
                    break
            finally:
                page += 1

        print("Fetched {} links".format(len(all_links)))
        return all_links

    def scrap_coin_data_from_page(self, link, id):
        driver = self._driver
        driver.get(link)
        date = driver.find_element_by_xpath("//div[contains(@class, 'auctioninfo')]//div[text()='Data']/../strong").text
        title = driver.find_element_by_xpath("//div[contains(@class, 'lotname')]/h1").text
        try:
            images = list(map(lambda el : el.get_attribute("href"),
                driver.find_elements_by_xpath("//div[contains(@class, 'img')]//a") +
                driver.find_elements_by_xpath("//div[@class='pic']/a")
                ))
        except Exception as e:
            images = []
        try: 
            desctiption = driver.find_element_by_xpath("//div[contains(@class, 'lotdescr')]").text
        except Exception as e:
            desctiption = ""
        
        desctiption = desctiption.replace("\n","\\")
        return {"title": title, "date": date, "description": desctiption, "images": images, "link": link }

