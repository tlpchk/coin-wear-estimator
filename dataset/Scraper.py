from selenium import webdriver
from abc import ABC, abstractmethod
import pandas as pd
import json
import ast
import urllib
import requests
import shutil

class Scraper(ABC):
    def __init__(self, base_url, name):
        self._base_url = base_url
        self._driver = webdriver.Chrome()
        self._name = name

    @abstractmethod
    def open_search_page(self, keyword: str):
        pass

    @abstractmethod
    def get_list_of_coin_urls(self, keyword: str):
        pass

    @abstractmethod
    def scrap_coin_data_from_page(self, link, csv_path):
        pass

    def link_of_coins_to_csv(self, keyword, csv_path):
        links = self.get_list_of_coin_urls(keyword)
        df = pd.DataFrame({"link": links})
        df.to_csv(csv_path, header=None, index=None)
        return df

    def scrap_coin_data(self, links, csv_path):
        try:
            df = pd.read_csv(csv_path, sep='|')
        except:
            df = pd.DataFrame()
        first_unscraped_link = len(df)
        for link in links[first_unscraped_link:]:
            data = self.scrap_coin_data_from_page(link)
            df = df.append(data, ignore_index=True)
            df.to_csv(csv_path, index=None, sep='|')
        return df

    def download_images(self, keyword):
        filename = keyword.lower().replace(" ","_")
        data_csv = "{}/data/{}.csv".format(self._name, filename) 
        img_dir= "{}/img".format(self._name)

        df = pd.read_csv(data_csv, sep='|')
        for i, image_array in df['images'].iteritems():
            image_array = ast.literal_eval(image_array)
            for j, image in enumerate(image_array):
                response = requests.get(image, stream=True)
                with open('{}/{}_{}.png'.format(img_dir, i+1, j+1), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                

    def pipeline(self, keyword, download_links = True):
        filename = "{}.csv".format(keyword.lower().replace(" ","_"))
        links_filename = "{}/links/{}".format(self._name, filename) 
        data_filename = "{}/data/{}".format(self._name, filename) 

        try:
            if download_links: 
                df = self.link_of_coins_to_csv(keyword, links_filename)
                links = list(df["link"])
            else:
                df = pd.read_csv(links_filename, header=None)
                links = list(df[0])
            self.scrap_coin_data(links, data_filename)
            self.download_images(keyword)
        except:
            pass
        
    def scroll_to_bottom(self):
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def quit(self):
        self._driver.quit()

    def __del__(self):
        self.quit()