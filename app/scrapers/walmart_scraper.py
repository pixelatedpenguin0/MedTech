from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class WalmartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.walmart.com/search"
    
    def get_price(self, medicine_name):
        """Get price for a medicine from Walmart"""
        search_url = f"{self.base_url}?q={medicine_name.replace(' ', '+')}"
        response = self._make_request(search_url)
        
        if not response:
            return {"price": None, "in_stock": False, "error": "Failed to fetch data"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first product price
        price_element = soup.find('span', {'class': 'price-characteristic'})
        in_stock_element = soup.find('span', {'class': 'product-available-store'})
        
        price = None
        if price_element:
            price = self.parse_price(price_element.text)
        
        in_stock = bool(in_stock_element and "In stock" in in_stock_element.text)
        
        return {
            "price": price,
            "in_stock": in_stock,
            "error": None
        } 