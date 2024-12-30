""" youtu.be/grB9QrjKSjw """

import json
from datetime import datetime as dt
import requests
import re
from art import tprint

HEADERS = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
    }

class WbReview:    
    def __init__(self, string: str):
        """ return wildberries reviews """
        self.item_name = None
        self.brand = None
        self.sku = self.get_sku(string=string)
        self.root_id = self.get_root_id(sku=self.sku)        

    @staticmethod
    def get_sku(string: str) -> str:
        if "wildberries" in string:
            pattern = r"\d{7,15}"
            sku = re.findall(pattern=pattern, string=string)
            if sku:
                return sku[0]
            else:
                raise Exception("Не удалось найти артикул")
        
        return string
    
    @staticmethod
    def write_json(data, path = None):
        with open(path, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def pcolor(text_code, color_num = 2):
        ''' color print '''
        print(f'\033[3{color_num}m{text_code}\033[0m', end='\n')
    
    def get_review(self) -> json:
        """ получение отзыва """
        url_review1 = f'https://feedbacks1.wb.ru/feedbacks/v2/{self.root_id}'
        url_review2 = f'https://feedbacks2.wb.ru/feedbacks/v2/{self.root_id}'
        response = requests.get(url=url_review1, headers=HEADERS)

        if response.status_code != 200:
            raise Exception("Не удалось получить данные!")
        
        if not response.json()['feedbacks']:            
            response = requests.get(url=url_review2, headers=HEADERS)
        
        if response.status_code != 200:
            raise Exception("Не удалось получить данные!")
        
        if not response.json()['feedbacks']:
            raise Exception("Данные не пришли!")

        return response.json()
    
    def get_root_id(self, sku: str) -> str:
        """ получение родителя id """
        url_root = f'https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1255987&spp=30&hide_dtype=10&ab_testing=false&nm={sku}'
        response = requests.get(url=url_root, headers=HEADERS)

        if response.status_code != 200:
            raise Exception("Не удалось получить данные!")
        
        root_id = response.json()["data"]["products"][0]["root"]
        self.item_name = response.json()["data"]["products"][0]["name"]
        self.brand = response.json()["data"]["products"][0]["brand"]

        return root_id

if __name__ == "__main__":    
    """ input start """
    tprint('.: wb-reviews :.', font='cybermedium', sep='\n')

    url = input("Enter url's: ")
    wb = WbReview(string=url)
    data_reviews = wb.get_review()

    wb.write_json(data_reviews, path=f'./json/{wb.sku}.json')

    wb.pcolor(f'🤖 {wb.item_name} / {wb.brand}', 3)    
    wb.pcolor(f'🙊 {data_reviews["valuation"]} / {data_reviews["valuationSum"]}', 3)

    for feedback in data_reviews["feedbacks"]:
        plus_min = '👎'
        color_ = 5      
        if int(feedback["productValuation"]) > 1:
            plus_min = '👍'
            color_ = 2

        if len(feedback["text"]) > 1:
            wb.pcolor(f'{plus_min} {feedback["text"]} / {feedback["productValuation"]}', color_)
        
        if len(feedback["pros"]) > 1:
            wb.pcolor(f'{plus_min} {feedback["pros"]} / {feedback["productValuation"]}', color_)