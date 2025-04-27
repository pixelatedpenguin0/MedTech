import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///medtech.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys (not required for basic functionality)
    OPENFDA_API_KEY = os.environ.get('OPENFDA_API_KEY')
    RXNORM_API_KEY = os.environ.get('RXNORM_API_KEY')
    
    # OCR Settings
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD') or r'C:\Program Files\Tesseract-OCR\tesseract.exe' 