from bs4 import BeautifulSoup
from requests import get, Session
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
import sys
import csv
import json
import lxml
import cchardet
import asyncio
import aiohttp
import time
import timeit

ACCEPTED_MERCHANTS = []
ASIN_VALUES = []
HEADERS = {}

with open("config.json") as config:
    data = json.load(config)
    ASIN_VALUES = data["asin"]
    ACCEPTED_MERCHANTS = data["accepted merchants"]
    HEADERS = data["headers"]

# Holds session information and provides functions to access desired page
class Amazon:
    def __init__(self):
        self.sess = Session()
        self.sess = CacheControl(self.sess, cache=FileCache('.web_cache'))
        self.headers = HEADERS
        self.sess.headers = self.headers
    
    def get_page(self, url):
        print("start")
        response = self.sess.get(url)
        print("stop")

        assert response.status_code == 200, f"{response.status_code}"
        
        result = BeautifulSoup(response.content, "lxml")
        
        return result


def generate_urls(asin_list):
    url_dict = {}
    for asin in asin_list:
        url_dict[asin]= f"https://www.amazon.com/dp/{asin}/"
    return url_dict

def get_tasks(session):
    tasks = {}
    for asin, url in generate_urls(ASIN_VALUES).items():
        tasks[asin] = asyncio.create_task(session.get(url, ssl=False))
    return tasks

async def main():
    with open('products.csv', 'w', newline='') as csvfile:
        fieldnames = ['ASIN', 'title', 'availability', 'price', 'valid merchant']  
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  
        writer.writeheader()
        
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            
            tasks = get_tasks(session)
            
            responses = await asyncio.gather(*tasks.values())
            
            for asin, response in zip(tasks.keys(), responses):
                
                page = BeautifulSoup(await response.text(), "lxml")
                
                is_available = None
                price = None
                valid_merchant = False
                product_title = page.find(id="productTitle").text.strip()
                
                # Checks for valid merchant
                if page.find(id="merchantID", attrs={"type":"hidden"}).attrs["value"] in ACCEPTED_MERCHANTS:
                    valid_merchant = True
                # Checks if in stock
                if page.find(id="buy-now-button"):
                    is_available = True
                    # Checks if price is given
                    if page.find(id="apex_offerDisplay_desktop"):
                        price = page.find(id="apex_offerDisplay_desktop").find(class_="a-offscreen").text 
                else:
                    is_available = False
                
                writer.writerow({'ASIN' : asin, 'title' : product_title, 'availability' : is_available, 'price' : price, 'valid merchant' : valid_merchant})
        
                
if __name__ == "__main__":
    t_start = timeit.default_timer()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main()) 
    t_stop = timeit.default_timer()

    print("Elapsed time: ", t_stop-t_start)