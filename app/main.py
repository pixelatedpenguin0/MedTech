from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio
from .scrapers.walmart_scraper import WalmartScraper
from .scrapers.costco_scraper import CostcoScraper
from .scrapers.riteaid_scraper import RiteAidScraper

app = FastAPI(title="Medicine Price Comparison API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MedicineRequest(BaseModel):
    medicine: str

class PriceResponse(BaseModel):
    walmart: Dict[str, Optional[float]]
    costco: Dict[str, Optional[float]]
    riteaid: Dict[str, Optional[float]]

@app.post("/compare-prices", response_model=PriceResponse)
async def compare_prices(request: MedicineRequest):
    """Compare medicine prices across different pharmacies"""
    try:
        # Initialize scrapers
        walmart_scraper = WalmartScraper()
        costco_scraper = CostcoScraper()
        riteaid_scraper = RiteAidScraper()
        
        # Get prices from all pharmacies
        walmart_result = walmart_scraper.get_price(request.medicine)
        costco_result = costco_scraper.get_price(request.medicine)
        riteaid_result = riteaid_scraper.get_price(request.medicine)
        
        return PriceResponse(
            walmart=walmart_result,
            costco=costco_result,
            riteaid=riteaid_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Medicine Price Comparison API"} 