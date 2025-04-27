from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class CostcoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.costco.com/CatalogSearch"
    
    def get_price(self, medicine_name):
        """Get price for a medicine from Costco"""
        search_url = f"{self.base_url}?dept=All&keyword={medicine_name.replace(' ', '+')}"
        response = self._make_request(search_url)
        
        if not response:
            return {"price": None, "in_stock": False, "error": "Failed to fetch data"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first product price
        price_element = soup.find('span', {'class': 'price'})
        in_stock_element = soup.find('span', {'class': 'out-of-stock'})
        
        price = None
        if price_element:
            price = self.parse_price(price_element.text)
        
        in_stock = not bool(in_stock_element)
        
        return {
            "price": price,
            "in_stock": in_stock,
            "error": None
        } 