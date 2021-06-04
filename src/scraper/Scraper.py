from selenium import webdriver
from abc import ABC, abstractmethod
import pandas as pd
from ..utils import get_filename, page_link_path, ROOT_PATH, raw_coins_path, create_dir_if_not_exist, metadata_path, raw_coins_path
import ast
import requests
from pathlib import Path
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
    def scrap_coin_data_from_page(self, link):
        pass

    def get_ds_path(self, keyword):
        return "{}/data/{}/{}".format(ROOT_PATH, self._name, get_filename(keyword))

    def link_of_coins_to_csv(self, keyword):
        csv_path = page_link_path(self.get_ds_path(keyword))
        links = self.get_list_of_coin_urls(keyword)
        create_dir_if_not_exist(csv_path)
        df = pd.DataFrame({"link": links})
        df.to_csv(csv_path, header=None, index=None)
        return df

    def scrap_coin_data(self, keyword):
        page_link_filename = page_link_path(self.get_ds_path(keyword))
        metadata_filename = metadata_path(self.get_ds_path(keyword))
        create_dir_if_not_exist(metadata_filename)

        try:
            df = pd.read_csv(metadata_filename, sep='|')
        except:
            df = pd.DataFrame()
        first_unscraped_link = len(df)
        links = pd.read_csv(page_link_filename, header=None)[0]
        for i, link in enumerate(links[first_unscraped_link:]):
            data = self.scrap_coin_data_from_page(link)
            data["id"] = i+first_unscraped_link+1
            df = df.append(data, ignore_index=True)
            df.to_csv(metadata_filename, index=None, sep='|')
        return df

    def download_images(self, keyword):
        metadata_filename = metadata_path(self.get_ds_path(keyword))
        raw_dir = raw_coins_path(self.get_ds_path(keyword))
        Path(raw_dir).mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(metadata_filename, sep='|')
        for i, image_array in df['images'].iteritems():
            image_array = ast.literal_eval(image_array)
            for j, image in enumerate(image_array):
                response = requests.get(image, stream=True)
                with open('{}/{}_{}.jpg'.format(raw_dir, i+1, j+1), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)


    def pipeline(self, keyword, download_links = True):
        if download_links:
            self.link_of_coins_to_csv(keyword)
        self.scrap_coin_data(keyword)
        self.download_images(keyword)
        
    def scroll_to_bottom(self):
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def quit(self):
        self._driver.quit()

    def __del__(self):
        self.quit()