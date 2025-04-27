import requests
from bs4 import BeautifulSoup
import time
import random
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _make_request(self, url, max_retries=2):
        """Make a request with retries and random delay"""
        for attempt in range(max_retries):
            try:
                # Add random delay between requests
                time.sleep(random.uniform(2, 3))
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {url} after {max_retries} attempts: {str(e)}")
                    return None
                time.sleep(random.uniform(1, 2))
        return None
    
    @abstractmethod
    def get_price(self, medicine_name):
        """Get price for a medicine from the pharmacy"""
        pass
    
    def parse_price(self, price_text):
        """Parse price text to float"""
        try:
            # Remove currency symbols and convert to float
            price = price_text.replace('$', '').replace(',', '').strip()
            return float(price)
        except (ValueError, AttributeError):
            return None 