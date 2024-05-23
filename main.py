from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from scraper import Scraper

app = FastAPI()
security = HTTPBearer()

# Dummy static token for authentication
API_TOKEN = "secret-token"

@app.get("/")
def read_root():
    return {"message": "Welcome to the scraper API"}

@app.get("/scrape")
def scrape(pages: int = 1, proxy: str = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validate token
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    scraper = Scraper(pages=pages, proxy=proxy)
    result = scraper.run()
    return {"scraped_data": result}



# from fastapi import FastAPI, HTTPException, Query
# from bs4 import BeautifulSoup
# import requests
# import json
# from typing import Optional
# from pathlib import Path
# from dotenv import load_dotenv
# import os
# import pdb  # Import pdb module

# # Load environment variables
# load_dotenv()

# app = FastAPI()

# # Define the base URL for the website to be scraped
# BASE_URL = "https://dentalstall.com/shop/"

# @app.get("/scrape")
# async def scrape_products(limit: Optional[int] = Query(None, description="Number of pages to scrape"), 
#                           proxy: Optional[str] = Query(None, description="Proxy server to use")):
#     products = []
#     page = 1

#     while True:
#         if limit and page > limit:
#             break

#         url = f"{BASE_URL}/page/{page}/"
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }
#         proxies = {
#             "http": proxy or os.getenv("PROXY_URL"),
#             "https": proxy or os.getenv("PROXY_URL")
#         } if proxy or os.getenv("PROXY_URL") else None

#         response = requests.get(url, headers=headers, proxies=proxies)
#         if response.status_code != 200:
#             raise HTTPException(status_code=500, detail=f"Error fetching page {page}: {response.status_code}")

#         soup = BeautifulSoup(response.text, "html.parser")
#         product_elements = soup.select(".product")

#         if not product_elements:
#             break

#         for product in product_elements:
#             title_element = product.select_one(".woo-loop-product__title a")
#             price_element = product.select_one(".woocommerce-Price-amount")
#             image_element = product.select_one(".mf-product-thumbnail img")

#             # pdb.set_trace()

#             if not title_element or not price_element or not image_element:
#                 continue

#             product_title = title_element.text.strip()
#             product_price = price_element.text.strip()
#             image_url = image_element["data-lazy-src"]

#             products.append({
#                 "product_title": product_title,
#                 "product_price": product_price,
#                 "image_url": image_url
#             })

#         page += 1

#     # Save products to a JSON file
#     output_file = Path("products.json")
#     with output_file.open("w") as f:
#         json.dump(products, f, indent=4)

#     return {"message": "Scraping completed successfully", "products": products}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
