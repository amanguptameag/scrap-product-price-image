import httpx
from bs4 import BeautifulSoup
import aiofiles
import json
import redis
import requests
from typing import List, Dict, Optional
import pdb
import os

class Scraper:
    def __init__(self, pages: int = 1, proxy: Optional[str] = None):
        self.pages = pages
        self.proxy = proxy
        self.base_url = "https://dentalstall.com/shop/"
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def fetch_page(self, url: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        proxies = {
            "http": self.proxy or os.getenv("PROXY_URL"),
            "https": self.proxy or os.getenv("PROXY_URL")
        } if self.proxy or os.getenv("PROXY_URL") else None

        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        return response.text

    def parse_page(self, content: str) -> List[Dict]:
        soup = BeautifulSoup(content, "html.parser")
        products = []
        product_elements = soup.select(".product")
        for element in product_elements:
            title_element = element.select_one(".woo-loop-product__title a")
            price_element = element.select_one(".woocommerce-Price-amount")
            image_element = element.select_one(".mf-product-thumbnail img")
            
            title = title_element.text.strip() if title_element else ""
            # pdb.set_trace()
            price = float(price_element.text.strip()[1:]) if price_element else 0.0
            image_url = image_element["data-lazy-src"] if image_element else ""

            products.append({
                "product_title": title,
                "product_price": price,
                "path_to_image": image_url
            })
        return products

    def run(self) -> List[Dict]:
        all_products = []
        for page in range(1, self.pages + 1):
            url = f"{self.base_url}page/{page}/"
            try:
                page_content = self.fetch_page(url)
                products = self.parse_page(page_content)
                all_products.extend(products)
            except httpx.RequestError as e:
                print(f"Request error: {e}")
            except httpx.HTTPStatusError as e:
                print(f"HTTP status error: {e}")
        
        self.save_to_file(all_products)
        print(f"Scraped {len(all_products)} products.")
        return all_products

    def save_to_file(self, data: List[Dict]):
        async def write_file():
            async with aiofiles.open("products.json", "w") as f:
                await f.write(json.dumps(data, indent=4))
        import asyncio
        asyncio.run(write_file())
