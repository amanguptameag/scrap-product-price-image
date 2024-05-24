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
    return {"product_count": len(result), "scraped_data": result}
