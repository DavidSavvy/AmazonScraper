from bs4 import BeautifulSoup
from requests import get, Session
import csv
import json

ACCEPTED_MERCHANTS = []
ASIN_VALUES = []

with open("config.json") as config:
    data = json.load(config)
    ASIN_VALUES = data["asin"]
    ACCEPTED_MERCHANTS = data["accepted merchants"]

# Holds session information and provides functions to access desired page
class Amazon:
    def __init__(self):
        self.sess = Session()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
            "Accept-Encoding": "gzip, deflate, br", 
            "Accept-Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        self.sess.headers = self.headers
    
    def get_page(self, url):
        response = self.sess.get(url)

        assert response.status_code == 200, f"{response.status_code}"

        result = BeautifulSoup(response.content, "html.parser")

        return result


def generate_urls(asin_list):
    url_dict = {}
    for asin in asin_list:
        url_dict[asin]= f"https://www.amazon.com/dp/{asin}/"
    return url_dict

def main():
    with open('products.csv', 'w', newline='') as csvfile:
        fieldnames = ['ASIN', 'title', 'availability', 'price', 'valid merchant']  
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  
        writer.writeheader()

        # Iterates through list of asin #s as urls
        for asin, url in generate_urls(ASIN_VALUES).items():
            # Probably don't need to create new object everytime
            amazon = Amazon()
            page = amazon.get_page(url)
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
    main()   
