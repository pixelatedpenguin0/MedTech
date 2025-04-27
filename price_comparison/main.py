from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="Medicine Price Comparison API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

class MedicineRequest(BaseModel):
    medicine: str

def get_goodrx_prices(medicine_name):
    # GoodRx API endpoint
    url = "https://api.goodrx.com/v1/prices"
    
    # You'll need to get an API key from GoodRx
    headers = {
        "Authorization": "Bearer YOUR_GOODRX_API_KEY",
        "Content-Type": "application/json"
    }
    
    params = {
        "name": medicine_name,
        "location": "US"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process the GoodRx data
        prices = []
        for pharmacy in data.get("pharmacies", []):
            prices.append({
                "pharmacy": pharmacy.get("name"),
                "price": pharmacy.get("price"),
                "in_stock": True,  # GoodRx only shows available prices
                "error": None
            })
        
        return prices
    except Exception as e:
        return [{
            "pharmacy": "Error",
            "price": None,
            "in_stock": False,
            "error": str(e)
        }]

@app.get("/")
async def root():
    template_path = os.path.join(BASE_DIR, "templates", "index.html")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail=f"Template file not found at {template_path}")
    return FileResponse(template_path)

@app.post("/compare-prices")
async def compare_prices(request: MedicineRequest):
    """Compare medicine prices using GoodRx API"""
    try:
        prices = get_goodrx_prices(request.medicine)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server at http://127.0.0.1:8080")
    print(f"Template directory: {os.path.join(BASE_DIR, 'templates')}")
    print(f"Static directory: {os.path.join(BASE_DIR, 'static')}")
    uvicorn.run(app, host="127.0.0.1", port=8080) 